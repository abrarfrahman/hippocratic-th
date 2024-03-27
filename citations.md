Initial Commit
**Testbench: 9/20**

v01: Implement RAG for textbook.txt
**Testbench: 14/20**
- Outline of RAG implementation: https://towardsdatascience.com/retrieval-augmented-generation-rag-from-theory-to-langchain-implementation-4e9bd5f6a4f2
- Resolve error with Pydantic: https://stackoverflow.com/questions/76313592/import-langchain-error-typeerror-issubclass-arg-1-must-be-a-class
- I had an old version of Langchain and they've moved a bunch of packages around: https://python.langchain.com/docs/expression_language/how_to/passthrough
- Chunks were too large: https://github.com/langchain-ai/langchain/discussions/3786
- Using a different package for OpenAI client: https://stackoverflow.com/questions/77505030/openai-api-error-you-tried-to-access-openai-chatcompletion-but-this-is-no-lon

v02: More complex matching
**Testbench: 16/20**
> The closest multiple choice answer to the generated response would be "could help make informed choices about medical treatment".
- This fails because OpenAI added extra text to the response.
- Also failing due to capitalization

