TWCC_CLI_CMD={{PUT_YOUR_TWCCLI_HERE}}

echo "1. Creating CCS"
$TWCC_CLI_CMD mk ccs -gpu 1 -wait -json > ccs_res.log

CCS_ID=$(cat ccs_res.log | jq '.id')
echo "2. CCS ID:" $CCS_ID

echo "3. Checking GPU"
ssh -o "StrictHostKeyChecking=no" `$TWCC_CLI_CMD ls ccs -gssh -s $CCS_ID` "nvidia-smi"

echo "4. RUN GPU"
ssh -o "StrictHostKeyChecking=no" `$TWCC_CLI_CMD ls ccs -gssh -s $CCS_ID` "./gpu-burn/gpu_burn"

echo "5. GC GPU"
$TWCC_CLI_CMD rm ccs -f -s $CCS_ID

echo "6. Checking CCS"
$TWCC_CLI_CMD ls ccs
