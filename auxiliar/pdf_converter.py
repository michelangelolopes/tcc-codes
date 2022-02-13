import pdfplumber

csv = open("arquivo_resultante.csv", "w")

with pdfplumber.open("arquivo_original.pdf") as pdf:
    for page in pdf.pages:
        table = page.extract_table() # tenta extrair os valores da página do pdf como se estivessem distribuídos em uma tabela
        
        for line in table:
            for string in line:
                if string == None:
                    string = "None"

                string = string.replace(".", "").replace(" ", "").strip() # remove pontos (normalmente falhas da extração) e espaços de uma string
                
                csv.writelines(string + "; ")
            
            csv.writelines("\n")

csv.close()