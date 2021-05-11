API_KEY=
PROJ_ID=
API_HST=ceph-taichung-default
API_URL="https://apigateway.twcc.ai/api/v3/$API_HST/projects/$PROJ_ID/key/"


get_project_code()
{
    API_PRJ="https://apigateway.twcc.ai/api/v2/$API_HST/projects/"

    curl -s -X GET \
      -H "x-api-key: $API_KEY" \
      -H "Content-Type: application/json" \
      -H "X-API-HOST: $API_HST" \
      $API_PRJ | jq .
}

list_s3_key()
{
    echo "1. Listing existing S3 keys"
    curl -s -X GET \
      -H "x-api-key: $API_KEY" \
      -H "Content-Type: application/json" \
      -H "X-API-HOST: $API_HST" \
      $API_URL | jq .
}

create_s3()
{
    echo "2. Creating Private S3 name= $1"
    curl -s -X POST \
      -H "x-api-key: $API_KEY" \
      -H "Content-Type: application/json" \
      -H "X-API-HOST: $API_HST" \
      -d "{\"name\":\"$1\"}" \
      $API_URL | jq .
}

reset_s3()
{
    echo "3. Reset S3 key for name= $1"
    curl -s -X PUT \
      -H "x-api-key: $API_KEY" \
      -H "Content-Type: application/json" \
      -H "X-API-HOST: $API_HST" \
      -d "{\"name\":\"$1\", \"all\": false}" \
      $API_URL | jq .
}

delete_s3()
{
    echo "4. Delete S3 key for name= $1"
    curl -s -X DELETE \
      -H "x-api-key: $API_KEY" \
      -H "Content-Type: application/json" \
      -H "X-API-HOST: $API_HST" \
      -d "{\"name\":\"$1\"}" \
      $API_URL | jq .
}

info_s3()
{
    BKT_URL="https://apigateway.twcc.ai/api/v3/$API_HST/projects/$PROJ_ID/buckets/?s3_name=$1&all=false"

    echo "5. Bucket Information for s3_name= $1"
    curl -s -X GET \
      -H "x-api-key: $API_KEY" \
      -H "Content-Type: application/json" \
      -H "X-API-HOST: $API_HST" \
      -d "{\"name\":\"$1\"}" \
      $BKT_URL | jq .
}

info_util_s3()
{
    BKT_URL="https://apigateway.twcc.ai/api/v3/$API_HST/projects/$PROJ_ID/buckets_util/?s3_name=$1&all=false"

    echo "6. Usage for s3_name= $1"
    curl -s -X GET \
      -H "x-api-key: $API_KEY" \
      -H "Content-Type: application/json" \
      -H "X-API-HOST: $API_HST" \
      -d "{\"name\":\"$1\"}" \
      $BKT_URL | jq .
}

get_project_code
list_s3_key
create_s3 "test"
list_s3_key
reset_s3 "test"
list_s3_key
info_s3 "test"
info_util_s3 "test"
delete_s3 "test"
