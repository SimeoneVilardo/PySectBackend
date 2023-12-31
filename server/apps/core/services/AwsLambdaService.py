import ast
import io
import zipfile
import boto3
import json
import time
from django.conf import settings
from server.apps.core.models import ChallengeSubmission


class AwsLambdaService:
    lambda_client = boto3.client("lambda")
    ecr_client = boto3.client("ecr")
    iam_client = boto3.client("iam")

    @classmethod
    def prepare_lambda_script(cls, challenge_submission: ChallengeSubmission) -> str:
        if challenge_submission.src_data is None:
            raise Exception("No src_data found in challenge submission")
        src_data = challenge_submission.src_data
        with open("server/apps/core/lambda/lambda_function.py", "r") as file:
            template = file.read()
        src_data = template.replace("###SRC###", src_data)
        return src_data

    @classmethod
    def validate_lambda_script(cls, src_file: str) -> bool:
        try:
            ast.parse(src_file)
        except Exception as e:
            return False
        return True

    @classmethod
    def create_zip(cls, input_file: str, src_file: str) -> io.BytesIO:
        in_memory_zip = io.BytesIO()
        with zipfile.ZipFile(in_memory_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zipf:
            input_info = zipfile.ZipInfo("input.json")
            input_info.external_attr = 0o777 << 16  # permissions -rwxrwxrwx
            zipf.writestr(input_info, input_file)

            src_info = zipfile.ZipInfo("lambda_function.py")
            src_info.external_attr = 0o777 << 16  # permissions -rwxrwxrwx
            zipf.writestr(src_info, src_file)

        in_memory_zip.seek(0)
        return in_memory_zip

    @classmethod
    def create_lambda_function(
        cls,
        function_name,
        zip_file,
        role_name=settings.AWS_LAMBDA_ROLE,
        handler="lambda_function.lambda_handler",
        runtime="python3.11",
        memory_size=128,
        timeout=10,
        env_vars=dict(),
    ):
        role = cls.iam_client.get_role(RoleName=role_name)
        response = cls.lambda_client.create_function(
            FunctionName=function_name,
            Runtime=runtime,
            Role=role["Role"]["Arn"],
            Handler=handler,
            Code={
                "ZipFile": zip_file.read(),
            },
            MemorySize=memory_size,
            Timeout=timeout,
            Environment={"Variables": env_vars},
        )
        return response

    @classmethod
    def wait_for_function_active(cls, function_name, timeout=30, interval=2):
        start_time = time.time()
        while True:
            response = cls.lambda_client.get_function(FunctionName=function_name)
            status = response["Configuration"]["State"]
            if status == "Active":
                break
            elif time.time() - start_time > timeout:
                raise Exception("Timeout while waiting for function to become active")
            time.sleep(interval)

    @classmethod
    def invoke_lambda_function(cls, function_name, payload=dict()):
        response = cls.lambda_client.invoke(
            FunctionName=function_name, InvocationType="Event", Payload=json.dumps(payload)
        )
        return response
