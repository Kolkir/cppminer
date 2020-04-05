#!/usr/bin/env bash
###########################################################
# Change the following values to preprocess a new dataset.
# BASE_PATH - script parameter point to the directory where data files are placed
# TRAIN_DATA_FILE, VAL_DATA_FILE and TEST_DATA_FILE should be paths to 
#   files containing files obtained from merge.py script
# DATASET_NAME is just a name for the currently extracted 
#   dataset.                                              
# MAX_DATA_CONTEXTS is the number of contexts to keep in the dataset for each 
#   method (by default 1000). At training time, these contexts
#   will be downsampled dynamically to MAX_CONTEXTS.
# MAX_CONTEXTS - the number of actual contexts (by default 200) 
# that are taken into consideration (out of MAX_DATA_CONTEXTS)
# every training iteration. To avoid randomness at test time, 
# for the test and validation sets only MAX_CONTEXTS contexts are kept 
# (while for training, MAX_DATA_CONTEXTS are kept and MAX_CONTEXTS are
# selected dynamically during training).
# SUBTOKEN_VOCAB_SIZE, TARGET_VOCAB_SIZE -   
#   - the number of subtokens and target words to keep 
#   in the vocabulary (the top occurring words and paths will be kept). 
# NUM_THREADS - the number of parallel threads to use. It is 
#   recommended to use a multi-core machine for the preprocessing 
#   step and set this value to the number of cores.
# PYTHON - python3 interpreter alias.
BASE_PATH=$1
OUT_PATH=$2
DATASET_NAME=dataset
MAX_DATA_CONTEXTS=1000
MAX_CONTEXTS=200
SUBTOKEN_VOCAB_SIZE=186277
TARGET_VOCAB_SIZE=26347
NUM_THREADS=64
PYTHON=python3
###########################################################

TRAIN_DATA_FILE=${BASE_PATH}/${DATASET_NAME}.train.c2s
VAL_DATA_FILE=${BASE_PATH}/${DATASET_NAME}.val.c2s
TEST_DATA_FILE=${BASE_PATH}/${DATASET_NAME}.test.c2s

mkdir -p ${OUT_PATH}/data
mkdir -p ${OUT_PATH}/data/${DATASET_NAME}

TARGET_HISTOGRAM_FILE=${OUT_PATH}/data/${DATASET_NAME}/${DATASET_NAME}.histo.tgt.c2s
SOURCE_SUBTOKEN_HISTOGRAM=${OUT_PATH}/data/${DATASET_NAME}/${DATASET_NAME}.histo.ori.c2s
NODE_HISTOGRAM_FILE=${OUT_PATH}/data/${DATASET_NAME}/${DATASET_NAME}.histo.node.c2s

echo "Creating histograms from the training data"
cat ${TRAIN_DATA_FILE} | cut -d' ' -f1 | tr '|' '\n' | awk '{n[$0]++} END {for (i in n) print i,n[i]}' > ${TARGET_HISTOGRAM_FILE}
cat ${TRAIN_DATA_FILE} | cut -d' ' -f2- | tr ' ' '\n' | cut -d',' -f1,3 | tr ',|' '\n' | awk '{n[$0]++} END {for (i in n) print i,n[i]}' > ${SOURCE_SUBTOKEN_HISTOGRAM}
cat ${TRAIN_DATA_FILE} | cut -d' ' -f2- | tr ' ' '\n' | cut -d',' -f2 | tr '|' '\n' | awk '{n[$0]++} END {for (i in n) print i,n[i]}' > ${NODE_HISTOGRAM_FILE}

${PYTHON} preprocess.py --train_data ${TRAIN_DATA_FILE} --test_data ${TEST_DATA_FILE} --val_data ${VAL_DATA_FILE} \
  --max_contexts ${MAX_CONTEXTS} --max_data_contexts ${MAX_DATA_CONTEXTS} --subtoken_vocab_size ${SUBTOKEN_VOCAB_SIZE} \
  --target_vocab_size ${TARGET_VOCAB_SIZE} --subtoken_histogram ${SOURCE_SUBTOKEN_HISTOGRAM} \
  --node_histogram ${NODE_HISTOGRAM_FILE} --target_histogram ${TARGET_HISTOGRAM_FILE} --output_name ${OUT_PATH}/data/${DATASET_NAME}/${DATASET_NAME}

# If all went well, the raw data files can be deleted, because preprocess.py creates new files 
# with truncated and padded number of paths for each example.
rm ${TARGET_HISTOGRAM_FILE} ${SOURCE_SUBTOKEN_HISTOGRAM} ${NODE_HISTOGRAM_FILE}

