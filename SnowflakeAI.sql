
------------------------------------------------------------
--- EXAMPLE: CLASSIFICATION FUNCTION
------------------------------------------------------------

create or replace temp table t as
select * from values
(‘212–555–1212’), (‘Denver’), (‘123 Main St.’) t(thing);

select
thing,
snowflake.cortex.CLASSIFY_TEXT(thing, [‘address’,’phone’,’city’])
from t;


------------------------------------------------------------
--- EXAMPLE: SENTIMENT ANALYSIS
------------------------------------------------------------

create or replace temp table t as
select * from values
(‘I hate this movie’), (‘The weather is gloomy today’), (‘What a relief’) t(thing);

select thing, snowflake.cortex.SENTIMENT(thing) from t;

------------------------------------------------------------
--- EXAMPLE: TRANSLATE FUNCTION
------------------------------------------------------------

SELECT
SNOWFLAKE.CORTEX.TRANSLATE(
$$
Zu meiner Familie gehören vier Personen. Die Mutter bin ich und dann gehört natürlich mein Mann dazu. Wir haben zwei Kinder, einen Sohn, der sechs Jahre alt ist und eine dreijährige Tochter.

Wir wohnen in einem kleinen Haus mit einem Garten. Dort können die Kinder ein bisschen spielen. Unser Sohn kommt bald in die Schule, unsere Tochter geht noch eine Zeit lang in den Kindergarten. Meine Kinder sind am Nachmittag zu Hause. So arbeite ich nur halbtags.

Eigentlich gehören zu unserer Familie auch noch die Großeltern. Sie wohnen nicht bei uns. Sie haben ein Haus in der Nähe. Die Kinder gehen sie oft besuchen
$$,
‘de’,
‘en’
);

------------------------------------------------------------
--- EXAMPLE: EXTRACT ANSWER
------------------------------------------------------------

SELECT
SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
$$
Mary had a little lamb. Her name was Sweety. It had white colored fur & long ears. Sweety loves to eat fresh grass & to play in fields.
$$,
‘What is the name of Marys lamb’
);

------------------------------------------------------------
--- EXAMPLE: COMPLETE FUNCTION
------------------------------------------------------------

SELECT SNOWFLAKE.CORTEX.COMPLETE('snowflake-arctic', 'What are top 2 free public email services?');


------------------------------------------------------------
--- EXAMPLE: VECTOR EMBEDDING
------------------------------------------------------------

SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m-v1.5', 'What are top 2 free public email services?');

---------------------------------------------------------------------------
--- EXAMPLE: CHECK STATUS of finetuning model. You need the Job ID
---------------------------------------------------------------------------

SELECT SNOWFLAKE.CORTEX.FINETUNE(
  'DESCRIBE',
  'ft_e7c079be-f011-4075-8f1f-f8e6c41375e7'
)
