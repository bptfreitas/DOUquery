1) Introdução

Este script consulta uma série de strings no Diário Oficial da União e envia um email com os resultados. O script requer que o usuário possua uma conta no gmail para enviar o email com os resultados ao destinatário. O login e a senha desta conta serão serão perguntados durante a execução do script.

2) Instalação

O script requer a instalação das bibliotecas BeautifulSoup, smtplib, e mechanize. No Ubuntu, isso pode ser feito com o comando:

$ sudo apt-get install python-bs4 python-mechanize

3) Utilização

Para que ele funcione minimamente, é necessário passar uma lista de strings de busca e o email do destinatário. Por exemplo, para buscar ocorrências dos nomes "Joãozinho" e "Mariazinha" e envia-las para o email "eumesmo@exemplo.com":

$ ./DOUquery --queries "Joãozinho" "Mariazinha" --email eumesmo@exemplo.com

O script por padrão irá buscar ocorrências entre o dia atual e o dia anterior. Para definir o dia inicial, utilize o parâmetro --inidate. Para definir o dia final de buscas, utilize o parâmetro --enddate. Utilize parâmetros no formato "dia/mês". Exemplo:

$ ./DOUquery --queries "Joãozinho" "Mariazinha" --email eumesmo@exemplo.com --inidate "04/02" --inidate "31/03"
