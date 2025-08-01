# Python Library
import logging
import os
import re
import uuid
# Custom Library
import config
# LLM Library
from langchain_ollama import OllamaLLM
# Md to Docx Library
from md2docx_python.src.md2docx_python import markdown_to_word

logging.basicConfig(format='%(asctime)s %(message)s', filename=config.log_path, level = config.log_level)

class DocumentGenerator():
    def __init__(self, model_name):
        # Ollama to trigger AI to response
        self.ollama_url = config.ollama_base_url
        self.ollama_model_name = model_name # "deepseek-r1:1.5b" TODO: Make sure model_name is selectable in the UI
        # md file generation folder
        self.md_doc_folder = config.md_doc_folder
        os.makedirs(self.md_doc_folder, exist_ok=True) # Do makedir to ensure that the folder is existed

    # Process to return boolean to know if this user query is requesting AI to generate a document
    def queryIntepreterDocGeneration(self, user_query):
        ollama_llm = OllamaLLM(base_url=self.ollama_url, model=self.ollama_model_name)
        prompt = f"""
            Analyze this query and respond with ONLY "True" or "False":
            - "True" if it requests document/template generation (e.g., "create a doc", "template for X").
            - "False" for general questions, explanations, or non-structured requests.

            Query: "{user_query}"
        """
        ai_response = ollama_llm(prompt)
        # Get AI response text
        if "deepseek" in self.ollama_model_name:
            ai_response = re.sub(r"<think>.*?</think>", "", ai_response, flags=re.DOTALL).strip()
        try:
            ai_response_bool = bool(ai_response)
        except Exception as ex:
            logging.error(str(ex))
            ai_response_bool = False
        return ai_response_bool
    
    def txtToDoc(self, ai_response, file_type = ".md", converted_file_type = '.docx'):
        random_filename = str(uuid.uuid4())
        file_name = random_filename + file_type
        file_path = os.path.join(self.md_doc_folder, file_name)
        with open(file_path, "w") as file:
            file.write(ai_response)
        #
        converted_file_name = random_filename + converted_file_type
        converted_file_path = os.path.join(self.md_doc_folder, converted_file_name)
        markdown_to_word(file_path, converted_file_path)
        return converted_file_path

if __name__ == "__main__":
    docGenerator = DocumentGenerator("deepseek-r1:1.5b")
    # user_query = "Can you generate a template for nutrionist plan?"
    # ai_response = docGenerator.queryIntepreterDocGeneration(user_query)
    # print(type(ai_response))
    # print(ai_response)

    # Assuming after the ai response is generated
    sample_ai_response = "Certainly! Here's a structured Microsoft Word template based on the provided context about diabetes care guidelines:\n\n---\n\n**Title: Developing a Comprehensive Diabetes Mellitus Care Plan**\n\n---\n\n### **Key Topics**\n\n#### 1. Introduction\nThis 2022 update of the American Association of Clinical Endocrinology (AACE) Clinical Practice Guideline provides evidence-based guidance for clinicians, diabetes-care teams, investigators, and others to manage diabetes effectively.\n\n#### 2. Key Topics\n\n##### **Healthcare Visits**\n- Access to care options for those with prediabetic or diabetic conditions.\n- Telemedicine as an accessible solution for remote healthcare.\n\n##### **Management at Work**\n- Management strategies for the workplace environment affecting diabetes management.\n- Collaboration between healthcare teams and employers.\n\n##### **Sleep Disorders**\n- Identification of sleep apnea syndromes (SAS) among diabetics.\n- Communication strategies to improve adherence and care.\n\n##### **Depression and Infertility**\n- Diagnoses related to diabetes and their impact on mental health.\n- Factors contributing to infertility in the context of diabetes.\n\n##### **Interdisciplinary Collaboration**\n- Importance of teamwork between healthcare providers, dietitians, and other specialists.\n\n##### **Metabolic Syndrome**\n- Connection of metabolic syndrome with diabetes and its management strategies.\n\n##### **Obesity**\n- Effects of obesity on diabetes and potential interventions.\n\n##### **Hospitalization for Diabetic Patients**\n- Proactive care measures when a patient is hospitalized due to diabetes.\n\n##### **Diabetic Nephropathies**\n- Management techniques to prevent complications associated with diabetic nephropathy.\n\n##### **Diabetic neuropathies**\n- Symptoms, diagnosis, and treatment options for diabetic neuropathy.\n\n##### **Diabetic Retinopathy**\n- Identification of retinopathy in diabetic individuals and management strategies.\n\n##### **Dyslipidemia**\n- Causes and management of dyslipidemias in the context of diabetes.\n\n##### ** guideline: Hospitalization; Hypertension; Hypoglycemia; Infertility; interdisciplinary communication; metabolic syndrome; obesity; prediabetic state; pregnancy; secondary diabetes; sleep apnea syndromes; telemedicine; vaccination**\n\n---\n\n### **Recommendations/Suggestions**\n1. **Healthcare Access and Telemedicine**\n   - Provide accessible care options, including telemedicine for remote healthcare providers.\n   - Encourage online discussions between patients and healthcare teams.\n\n2. **Sleep Hygiene**\n   - Promote good sleep hygiene to support prediabetic health.\n   - Offer personalized advice on reducing SAS symptoms.\n\n3. **Interdisciplinary Collaboration**\n   - Foster teamwork among healthcare teams, dietitians, and specialists.\n   - Regular check-ins to ensure coordinated care.\n\n4. **Educational Resources**\n   - Provide resources for diabetics, including mental health support and diabetes education.\n   - Share case studies of successful care plans in the context of diabetes.\n\n5. **Monitor for SAS**\n   - Early identification of SAS among diabetics through lifestyle changes and management practices.\n   - Collaborative efforts to address SAS before significant medical complications arise.\n\n6. **Symptoms and Diagnosis**\n   - Document symptoms and conditions related to prediabetic state, including diabetes and dyslipidemia.\n   - Provide guidelines for proper diagnosis in the context of diabetes.\n\n7. **Treatment Management**\n   - Present management options with evidence-based guidance.\n   - Encourage discussions among professionals on effective treatment strategies.\n\n8. **Patient Education**\n   - Educate patients about the link between lifestyle choices and prediabetic health.\n   - Highlight potential interventions for prediabetes and diabetes in the context of their care plans.\n\n---\n\nThis template provides a clear, structured approach to guiding healthcare professionals and their teams in managing diabetes effectively, ensuring comprehensive coverage of all relevant areas."

    mdDocFile = docGenerator.txtToDoc(sample_ai_response)
