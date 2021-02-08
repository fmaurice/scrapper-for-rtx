import os
from requests_html import HTMLSession
from colorama import Fore, Back, Style 
import datetime
from email.mime.text import MIMEText
from subprocess import Popen, PIPE
from selenium import webdriver
from pyvirtualdisplay import Display 

class ScraperForRTX:

    messages = []
    currPath = os.path.dirname(os.path.abspath(__file__))
    URL_FOR_TOP_ACHAT = 'https://www.topachat.com/pages/produits_cat_est_micro_puis_rubrique_est_wgfx_pcie_puis_mc_est_rtx%252B3080.html'
    URL_FOR_LDLC = 'https://www.ldlc.com/informatique/pieces-informatique/carte-graphique-interne/c4684/+fv121-19183.html'

    def start(self):
        outOfStock = self.checkTopAchatPage()
        outOfStock = self.checkLDLCPage()

        if not outOfStock:
            self.sendEmail()
        else:
            self.printok('All is out of stock')

    def checkTopAchatPage(self):
        self.printok ("Top Achat page...")
        # No JS needed here
        outOfStock = True
        session = HTMLSession()

        r = session.get(self.URL_FOR_TOP_ACHAT)
        sections = r.html.find('.grille-produit section')

        for section in sections:
            if 'class' in section.attrs:
                if not 'en-rupture' in section.attrs['class']:
                    self.printnok(section.text)
                    self.printnok("*** Link : %s" % list(section.absolute_links)[0])
                    outOfStock = False

        return outOfStock

    def checkLDLCPage(self):
        self.printok ("LDLC page...")
        # JS Needed here
        outOfStock = True

        display = Display(visible=0, size=(1024, 768)) 
        display.start()


        driver = webdriver.Chrome(executable_path= self.currPath + '/chromedriver', 
            service_args=['--verbose', '--log-path=' + self.currPath + '/chromedriver.log'])

        driver.get(self.URL_FOR_LDLC)

        
        listing = driver.find_elements_by_css_selector('.listing-product li')
        for listElement in listing:
            element = listElement.find_element_by_css_selector('.stocks .modal-stock-web .modal-stock-web')
            if element.text != 'RUPTURE':
                self.printnok(listElement.text)
                self.printnok("*** Link : %s" % listElement.find_element_by_tag_name('a').get_attribute('href'))
                outOfStock = False

        return outOfStock

    def sendEmail(self):
        p = Popen(["/usr/bin/mail", "-s", '"RTX 3080 watcher"', 'root'], stdin=PIPE)
        strMessage = "\n".join(self.messages)
        p.communicate(strMessage)
        self.printnok("Email sended")

    def printok(self, message):
        self.messages.append(message)
        now = datetime.datetime.now()
        print (Fore.GREEN + now.strftime('%Y-%m-%d %H:%M:%S') + ' ' + message)

    def printnok(self, message):
        self.messages.append(message)
        now = datetime.datetime.now()
        print (Fore.RED + now.strftime('%Y-%m-%d %H:%M:%S') + ' ' + message)    



if __name__ == "__main__":
    scraperForRTX = ScraperForRTX()
    scraperForRTX.start()
