import os
from requests_html import HTMLSession
from colorama import Fore, Back, Style 
import datetime
from subprocess import Popen, PIPE
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from pyvirtualdisplay import Display 
import smtplib
from email.mime.text import MIMEText
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

class ScraperForRTX:

    messages = []
    outOfstock = True
    screenshotFullNames = []
    currPath = os.path.dirname(os.path.abspath(__file__))
    URL_FOR_TOP_ACHAT = 'https://www.topachat.com/pages/produits_cat_est_micro_puis_rubrique_est_wgfx_pcie_puis_mc_est_rtx%252B3080.html'
    URL_FOR_LDLC = 'https://www.ldlc.com/informatique/pieces-informatique/carte-graphique-interne/c4684/+fv121-19183.html'
    URL_FOR_FNAC = 'https://www.fnac.com/SearchResult/ResultList.aspx?SCat=8!1%2c8006!2&Search=RTX3080&sft=1&sl'
    

    def start(self):
        
        self.checkTopAchatPage()
        self.checkLDLCPage()
        self.checkFNACPage()

        if not self.outOfstock:
            self.sendEmail()
        else:
            self.printok('All is out of stock')

    def checkTopAchatPage(self):
        self.printok ("Top Achat page...")
        # No JS needed here
        session = HTMLSession()

        try:
            r = session.get(self.URL_FOR_TOP_ACHAT)
            sections = r.html.find('.grille-produit section')

            if len(sections) == 0:
                raise Exception('Element not found in the page')

            for section in sections:
                if 'class' in section.attrs:
                    if not 'en-rupture' in section.attrs['class']:
                        msg = section.text + "\n"
                        msg = msg + "*** Link : %s" % list(section.absolute_links)[0]
                        raise NoSuchElementException(msg)
        except Exception as e:
            self.printnok("Something goes wrong : " + str(e))
            self.outOfstock = False

    def checkLDLCPage(self):
        self.printok ("LDLC page...")
        # JS Needed here

        display, driver = self.getDisplayAndDriver()

        driver.get(self.URL_FOR_LDLC)

        try:        
            listing = driver.find_elements_by_css_selector('.listing-product li')

            if len(listing) == 0:
                raise Exception('Element not found in the page')

            for listElement in listing:
                element = listElement.find_element_by_css_selector('.stocks .modal-stock-web .modal-stock-web')
                if element.text != 'RUPTURE':
                    msg = listElement.text + "\n*** Link : %s\n" % listElement.find_element_by_tag_name('a').get_attribute('href')
                    raise NoSuchElementException(msg)
                    
        except Exception as e:
            self.printnok("Something goes wrong : " + str(e))
            self.outOfstock = False
            self.takeScreenShot(driver, 'ldlc')

        display.stop()

    def checkFNACPage(self):
        self.printok ("FNAC page...")
        # JS Needed here

        display, driver = self.getDisplayAndDriver()

        driver.get(self.URL_FOR_FNAC)

        try:        
            listing = driver.find_elements_by_css_selector('.Article-itemGroup')

            if len(listing) == 0:
                raise Exception('Element not found in the page')

            for listElement in listing:
                element = listElement.find_element_by_css_selector('.Article-itemInfo .moreInfos-table .shipping')              
                try:
                    element.find_element_by_css_selector('.Nodispo')
                except NoSuchElementException as e:
                    e.message = listElement.text + "\n*** Link : %s\n" % listElement.find_element_by_tag_name('a').get_attribute('href')
                    raise

        except Exception as e:
            self.printnok("Something goes wrong : " + str(e))
            self.outOfstock = False
            self.takeScreenShot(driver, 'fnac')

        display.stop()

    def getDisplayAndDriver(self):
        display = Display(visible=0, size=(1024, 1024*2)) # for the screenshot
        display.start()

        option = webdriver.ChromeOptions()
        # For ChromeDriver version 79.0.3945.16 or over
        option.add_argument('--disable-blink-features=AutomationControlled')
        # Browser fingerprint 
        option.add_argument("window-size=1280,800")
        option.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36")
        
        driver = webdriver.Chrome(executable_path= self.currPath + '/chromedriver', 
            service_args=['--verbose', '--log-path=' + self.currPath + '/chromedriver.log'],
            options=option)

        return display, driver

    def sendEmail(self):
        strMessage = "\n".join(self.messages)
        msg = MIMEMultipart()
        msg.attach(MIMEText(strMessage))
        msg['Subject'] = 'RTX 3080 scrapper'
        msg['To'] = 'root'

        # attach the screenshot
        for filename in self.screenshotFullNames:
            part = MIMEBase('application', "octet-stream")
            part.set_payload(open(filename, "rb").read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(os.path.basename(filename)))
            msg.attach(part)

        s = smtplib.SMTP('localhost')
        s.sendmail('', 'root', msg.as_string())
        s.quit()
        self.printnok("Email sended")

    def takeScreenShot(self, driver, strFrom):
        now = datetime.datetime.now()
        screenshotFullName = self.currPath + '/screenshots/screenshot-' + strFrom + '-' + now.strftime('%Y%m%d-%H%M%S') + '.png'
        driver.save_screenshot(screenshotFullName)
        self.screenshotFullNames.append(screenshotFullName)


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
