1) Introdução
Este script consulta uma série de strings no Diário Oficial da União e envia um email com os resultados.

2) Instalação

O script requer a instalação das bibliotecas BeautifulSoup, smtplib, e mechanize. No Ubuntu, isso pode ser feito com o comando:
$ sudo apt-get install python-bs4 python-mechanize

3) Utilização

Para que ele funcione minimamente, é necessário passar uma lista de strings de busca e o email do destinatário. Por exemplo:\n
$ ./DOUquery --queries "Joãozinho" "Mariazinha" --email eumesmo@exemplo.com

O script por padrão irá buscar ocorrências entre o dia atual e o dia anterior. Para definir o dia inicial, utilize o parâmetro --inidate. Para definir o dia final de buscas, utilize o parâmetro --enddate. Utilize parâmetros no formato "dia/mês". Exemplo:\n
$ ./DOUquery --queries "Joãozinho" "Mariazinha" --email eumesmo@exemplo.com --inidate "04/02" --inidate "31/03"
