#!/bin/bash
conda create -n trader python=3.10
conda activate trader
pip install lumibot timedelta alpaca-trade-api==3.1.1
pip install torch torchvision torchaudio transformers