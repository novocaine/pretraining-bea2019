from __future__ import print_function, unicode_literals, division

import argparse
import os
import os.path
import subprocess
import sys
import time
import uuid

from websocket import create_connection

MARIAN = "./tools/marian-dev/build"

class GrammarClient:
    def __init__(self, port, batch_size):
        self.port = port
        self.batch_size = batch_size
        self.ws = self.create_ws()

    def create_ws(self):            
        return create_connection("ws://localhost:{}/translate".format(self.port))

    def send_batch(self, batch):        
        try:
            self.ws.send(batch)
        except (BrokenPipeError, IOError):
            self.ws = self.create_ws()
            self.ws.send(batch)
        return self.ws.recv()

    def translate(self, input_strings):
        print("Calling server...", file=sys.stderr)
        output_strings = []
        count = 0
        batch = ""
        for line in input_strings:            
            line += "\n"
            count += 1
            batch += line.decode('utf-8') if sys.version_info < (3, 0) else line
            if count == self.batch_size:
                # translate the batch
                result = self.send_batch(batch)
                output_strings.append(result.rstrip())
                count = 0
                batch = ""

        if count:
            # translate the remaining sentences
            result = self.send_batch(batch)
            output_strings.append(result.rstrip())

        print(output_strings, file=sys.stderr)
        return output_strings


def rerank(output_prefix, model):
    print("Re-ranking...", file=sys.stderr)
    # Re-rank the n-best list
    with open(f"{output_prefix}.nbest4") as nbest4:
        output_list = subprocess.run(["python", "./tools/rescore.py",
                                      "-c", f"{model}/rescore.ini",
                                      "-t", 
                                      "-n", "1.0"], stdin=nbest4, stdout=subprocess.PIPE)
        return output_list.stdout.decode("utf-8").split("\n")[:-1]


def rescore(model, marian_args, input_strings, client_output):
    print("Rescoring...", file=sys.stderr)

    input_filename = "input." + str(uuid.uuid4())
    with open(input_filename, "w") as input_file:
        input_file.write("\n".join(input_strings))

    output_prefix = "output." + str(uuid.uuid4())
    client_output_filename = output_prefix + ".nbest0"
    with open(client_output_filename, "w") as client_output_file:
        client_output_file.write("\n".join(client_output))

    # Re-score the n-best list with each right-to-left model
    try:
        for i in range(1, 5):
            output_filename = f"{output_prefix}.nbest{i-1}"
            assert os.path.exists(output_filename)
            args = [f"{MARIAN}/marian-scorer",
                "-m", f"{model}/rl{i}.npz",
                "-v", f"{model}/vocab.spm", f"{model}/vocab.spm",
                "--n-best",
                "--n-best-feature", f"R2L{i}",
                "--workspace", "3000",
                "--mini-batch-words", "4000", 
                "-t", input_filename,
                output_filename,
                "--log", output_filename + ".log"]
            result = subprocess.run(args, check=True, stdout=subprocess.PIPE)
            with open(f"{output_prefix}.nbest{i}", "wb") as output_nbest:
                output_nbest.write(result.stdout)

        return rerank(output_prefix, model)
    finally:
        if False:
            for i in range(1, 5):
                try:
                    os.unlink(f"{output_prefix}.nbest{i}")
                except:
                    pass


def translate(client, input_strings, model, marian_args):
    client_output = client.translate(input_strings)
    return rescore(model, marian_args, input_strings, client_output)


if __name__ == "__main__":
    # handle command-line options
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--batch-size", type=int, default=1)
    parser.add_argument("-p", "--port", type=int, default=8080)
    parser.add_argument("input_file", type=str)
    parser.add_argument("model", type=str)
    parser.add_argument("--marian-args", type=str, default="")
    args = parser.parse_args()
    client = GrammarClient(args.port, args.batch_size)
    print("\n".join(translate(client, list(open(args.input_file)), args.model, args.marian_args.split(" "))))
