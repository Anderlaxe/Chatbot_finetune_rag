from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
from time import sleep, time
import undetected_chromedriver as uc
from fake_useragent import UserAgent
import os
import tkinter as tk
from selenium.webdriver.common.action_chains import ActionChains

INIT_PROMPT = "Bonjour, tu es un développeur chargé de créer un dataset d'entrainement pour une IA. Voici ta mission, que tu dois impérativement respecter de manière scrupuleuse : Il te sera joint une documentation, la première partie de ton travail consiste à en tirer une liste synthétique mais exhaustive de toutes les informations en son sein. Ensuite, tu devras jouer le rôle d'une personne qui pose des questions. Ces questions devront être en lien avec les sujets évoqués dans la documentation, mais doivent provenir d'une personne qui n'en a pas connaissance. Elles peuvent donc être très spécifiques, ou très vagues, tant qu'il serait possible à une personne de faire le lien entre la question posée, et l'intérêt de la documentation pour y répondre. Ensuite, tu devras jouer le rôle d'un chatbot ayant connaissance de la documentation, et pouvant répondre aux questions posées. Cette mission te convient-elle ? Elle est d'une importance cruciale"
DOC_PROMPT = "Voici la documentation en question, génère la liste des informations qui s'y trouvent : \n\n"
QUESTION_PROMPT = "Très bien, maintenant, génère un ensemble de questions qu'une personne pourrait se poser, en rapport avec cette documentation. Elles ne doivent pas venir de la lecture de cette liste, mais venir d'une personne qui se poserait des questions sur les sujets évoqués. Il est donc possible que parmi ces questions, certaines n'aient pas de réponses ou soient hors sujet Il faut aussi tenir compte que les personnes sont peu informées sur le sujet, et s'expriment dans un langage courant, en évitant généralement les termes techniques et jargonneux qui peuvent être présents. Une bonne question devrait idéalement pouvoir être indissociable avec un extrait de conversation de la vie de tous les jours pour un étudiant ou un professeur."
ANSWER_PROMPT = "Très bien, maintenant ta mission consiste à jouer le rôle d'un chatbot pour répondre à ces questions. Pour chacune des questions précédentes, émet une réponse dans un langage formel, utilisant le vouvoiement, qui permette d'éclairer l'utilisateur concernant son interrogation. Il est impératif que la réponse ne contienne que des éléments d'information issus de la documentation, il est strictement interdit d'émettre des hypothèses ou d'utiliser d'autres sources d'information que celles présentes dans la documentation. Si il arrivait qu'une question ne trouve pas de réponse dans les informations que tu as analysées, il te faudra alors répondre que tu ne sais pas, ou demander à l'utilisateur des précisions supplémentaires pour être le plus complet et utile possible. Génère ces réponses dans un format standard JSON, en un unique fichier qui les regroupe toutes (sous forme de liste d'objets identiques contenant une 'question' et une 'answer'), et réponds à toutes celles que tu as imaginées plus haut."

path = chromedriver_autoinstaller.install()

op = webdriver.ChromeOptions()
op.add_argument(f"user-agent={UserAgent.random}")
op.add_argument("user-data-dir=./")
op.add_experimental_option("detach", True)
op.add_experimental_option("excludeSwitches", ["enable-logging"])

driver = uc.Chrome(chrome_options=op, driver_executable_path=path)

def write_prompt(prompt, inputElements):
    prompt = prompt.replace("\t", "    ")
    for line in prompt.split("\n"):
        inputElements[0].send_keys(line)
        inputElements[0].send_keys(Keys.SHIFT, Keys.ENTER)
        sleep(0.001)

#Login
driver.get('https://chat.openai.com/auth/login')
sleep(1)
inputElements = driver.find_elements(By.TAG_NAME, "button")
inputElements[0].click()
input("Press ENTER when you're ready")

dataset_files = [x for x in os.listdir("./dataset") if x.endswith(".json")]
files_to_process = [x for x in os.listdir("./pages") if x.endswith(".md") and x[:-3] + ".json" not in dataset_files]
files_to_process.sort()

startTime = time()

for filename in files_to_process:
    doc = ""
    if filename.endswith(".md"):
        with open("./pages/" + filename, "r") as f:
            doc = f.read()
            if doc == "":
                continue
        print("Processing " + filename)
        try:
            flag = "init"
            inputElements = driver.find_elements(By.TAG_NAME, "textarea")
            
            write_prompt(INIT_PROMPT, inputElements)
            WebDriverWait(driver, 120).until(EC.visibility_of_element_located((By.XPATH, "//button[@data-testid='send-button']")))
            inputElements[0].send_keys(Keys.ENTER)
            

            sleep(1)
            formattedPrompt = DOC_PROMPT + doc
            write_prompt(formattedPrompt, inputElements)
            WebDriverWait(driver, 120).until(EC.visibility_of_element_located((By.XPATH, "//button[@data-testid='send-button']")))
            inputElements[0].send_keys(Keys.ENTER)

            sleep(1)
            write_prompt(QUESTION_PROMPT, inputElements)
            WebDriverWait(driver, 120).until(EC.visibility_of_element_located((By.XPATH, "//button[@data-testid='send-button']")))
            inputElements[0].send_keys(Keys.ENTER)

            sleep(1)
            write_prompt(ANSWER_PROMPT, inputElements)
            WebDriverWait(driver, 120).until(EC.visibility_of_element_located((By.XPATH, "//button[@data-testid='send-button']")))
            inputElements[0].send_keys(Keys.ENTER)

            flag = "response"
            #Wait for response
            sleep(10)
            WebDriverWait(driver, 120).until(EC.visibility_of_element_located((By.XPATH, "//button[@data-testid='send-button']")))

            # allow max 2 continue generating
            generating = driver.find_elements(By.XPATH, "//button[@as='button']")
            if len(generating) > 0:
                generating[0].click()
                sleep(40)
            generating = driver.find_elements(By.XPATH, "//button[@as='button']")
            if len(generating) > 0:
                generating[0].click()
                sleep(20)

            copy_button = driver.find_elements(By.XPATH, "//button[text()='Copy code']")[0]
            driver.execute_script("arguments[0].scrollIntoView({ block: 'center' });", copy_button)

            sticky = driver.find_elements(By.CLASS_NAME, "sticky")[0]
            driver.execute_script("arguments[0].remove();", sticky)
            sleep(1)
            driver.execute_script("arguments[0].focus();", copy_button)
            sleep(1)
            copy_button.send_keys(Keys.ENTER)
            sleep(1)
            
            root = tk.Tk()
            final_json = root.clipboard_get()
            root.destroy()

            with open("./dataset/" + filename[:-3] + ".json", "w") as f:
                f.write(final_json)

        except Exception as e:

            print("--- Error on " + filename)
            print(e)
            sleep(1)
            if (flag == "init"):
                print("--- Got rate limited ")
                stopTime = time()
                elapsedTime = stopTime - startTime
                print("--- Time elapsed : " + str(elapsedTime) + "s")
                print("--- Sleeping for 180s")
                sleep(180)
                startTime = time()

        driver.get('https://chat.openai.com/auth/login')
        sleep(1)
        driver.switch_to.active_element.send_keys(Keys.ENTER)
        sleep(1)

    else:
        continue