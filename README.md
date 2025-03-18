# Snowflake-AI
 Contains the AI queries for Snowflake

# How to upload LLM models into Snowflake
You may upload your own LLM models in Snowflake stage. In my case, there was a models.zip (410 MB) file containing - tokenizer, pytorch_model.bin among other jsons. So I had to upload the zip to snowflake stage using SnowSQL. Why? because using the web UI, only 250 MB files can be uploaded. So used the PUT command to upload the models.zip
After this, you need to unzip the file in Snowflake notebook's working directory. Then you can use the pytorch_model.bin in your training code

