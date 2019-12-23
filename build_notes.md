Building Marian
===============

On Deep Learning AMI (Ubuntu 16.04) Version 26.0 (ami-025ed45832b817a35).

Follow instructions in https://marian-nmt.github.io/docs/ for Ubuntu 16.04 and the 'SentencePiece' steps. Install own version of protobuf
as the system one is too far ahead.

The link to protobuf 2.6.1 is broken so download protobuf from https://github.com/protocolbuffers/protobuf/releases/tag/v2.6.1 and build it manually in ~/protobuf as per instructions.

make -j fails with a memory error (even on a 16GB instance) so do make -j1 and wait for ages.

copied the marian dir into ~/pretraining-bea2019/systems/tools/marian-dev

