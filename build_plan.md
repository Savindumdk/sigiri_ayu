I want to generate a RAG Chatbot that has the capability that first asks simple questions from the user in a flow and then suggests the best product based on the provided information. And also the user can ask about the products, the product details and about the brand. When suggesting items, it must provide the relevant product image aswell. 

Brand Details: Sigiri_Ayu_Details.md
Product Details: Sigiri_Ayu_Product_Descriptions
Images: has the images related to the specific item in its respective name already renamed.
Mascot: has the mascot image and the animation to be used.

my python version is 3.10.9, use a virtual environment and build this but properly update the requirements. I want to build this using streamlit so i can deploy it in streamlit community cloud free version. So i will create a public repo in the github once the system built and then upload it to streamlit cloud from there.

Make the background white of the application and more modern looking appeal with the mascot and how the mascot reacts to each message.

Make the application mobile responsive aswell.

For the LLM use the Gemini API Key and for the embedding model if needed use something open source or faster as this will be deployed in free server it must be optimized. ive created the .env file and placed the gemini_api_key.

When building the RAG since it needs brand, product details and images to be loaded at the right moment its better to have an optimized way that you decide because it needs to be deployed in free server.

Based on your decisions decide whether to use langchain, autogen, or something else or just python based on the needs as the application must simpler, modern and optimized for the free server. 

Also Build a memory for the chat session, so it answers based on its chat.

Then create test files and test the system and provide a complete running system.
