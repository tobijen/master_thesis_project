import argparse
import os
from typing_extensions import Optional

from dotenv import load_dotenv
import openai
from openai import AzureOpenAI, OpenAI
from retry import retry
from tqdm import tqdm

from umbrela_models.llm_judge import LLMJudge
from umbrela_models.utils import common_utils

load_dotenv() # Load environment variables from .env file

# Select relevance categories to be judged.
JUDGE_CAT = [0, 1, 2, 3]


class GPTJudge(LLMJudge):
    def __init__(
        self,
        qrel: str,
        model_name: str,
        prompt_file: Optional[str] = None,
        prompt_type: Optional[str] = "bing",
        few_shot_count: int = 0,
    ) -> None:
        super().__init__(qrel, model_name, prompt_file, prompt_type, few_shot_count)
        self.create_openai_client()

    def create_openai_client(self):
        api_key = os.environ["OPENAI_KEY"]

        self.client = OpenAI(api_key=api_key)
        self.engine = self.model_name

    @retry(tries=3, delay=0.1)
    def run_gpt(self, prompt, max_new_tokens):
        # messages = [
        #     {"role": "system", "content": "You are a helpful assistant."},
        #     {"role": "user", "content": prompt},
        # ]
        # try:
        #     response = self.client.chat.completions.create(
        #         model=self.engine,
        #         messages=messages,
        #         max_completion_tokens=max_new_tokens,
        #         top_p=1,
        #         presence_penalty=0,
        #     )
        #     print("RESPONSE RAW: ", response)
        #     output = (
        #         response.choices[0].message.content.lower()
        #         if response.choices[0].message.content
        #         else ""
        #     )

        # except openai.BadRequestError as e:
        #     print(f"Encountered {e} for {prompt}")
        #     output = ""
        # return output

        response = self.client.responses.create(
            model=self.engine,
            reasoning={"effort": "low"},
            # temperature=0,
            # top_p=0.5,
            text={"verbosity": "low"},
            input=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.output_text

    def predict_with_llm(
        self,
        request_dict: list,
        max_new_tokens: int,
        prepocess: bool,
    ):
        if prepocess:
            self.query_passage = common_utils.preprocess_request_dict(request_dict)
        else:
            self.query_passage = request_dict
        self.prompts = common_utils.generate_prompts(
            self.query_passage,
            #self.prompt_examples, 
            self._prompt_template
        )

        outputs = [
            self.run_gpt(prompt, max_new_tokens) for prompt in tqdm(self.prompts)
        ]

        print("OUTPUTS: ", outputs)
        return outputs

    def judge(self, request_dict, max_new_tokens=100, prepocess: bool = True):
        outputs = self.predict_with_llm(request_dict, max_new_tokens, prepocess)
        return common_utils.prepare_judgments(
            outputs, self.query_passage, self.prompts, self.model_name
        )


# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--qrel", type=str, help="qrels file", required=True)
#     parser.add_argument("--result_file", type=str, help="retriever result file")
#     parser.add_argument("--prompt_file", type=str, help="prompt file")
#     parser.add_argument(
#         "--prompt_type", type=str, help="Prompt type. Supported types: [bing, basic]."
#     )
#     parser.add_argument("--model", type=str, help="model name")
#     parser.add_argument(
#         "--few_shot_count", type=int, help="Few shot count for each category."
#     )
#     parser.add_argument("--num_sample", type=int, default=1)
#     parser.add_argument("--regenerate", action="store_true")

#     args = parser.parse_args()
#     load_dotenv()

#     judge = GPTJudge(
#         args.qrel, args.model, args.prompt_file, args.prompt_type, args.few_shot_count
#     )
#     judge.evalute_results_with_qrel(
#         args.result_file,
#         regenerate=args.regenerate,
#         num_samples=args.num_sample,
#         judge_cat=JUDGE_CAT,
#     )


# if __name__ == "__main__":
#     main()
