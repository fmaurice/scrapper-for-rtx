from requests_html import HTMLSession
from colorama import Fore, Back, Style 
import datetime
from email.mime.text import MIMEText
from subprocess import Popen, PIPE


class ScraperForRTX:

    messages = []
    outOfStock = True

    def start(self):

        session = HTMLSession()

        # Top achat page
        self.printok ("Top Achat page")

        r = session.get('https://www.topachat.com/pages/produits_cat_est_micro_puis_rubrique_est_wgfx_pcie_puis_mc_est_rtx%252B3080.html')
        sections = r.html.find('.grille-produit section')

        for section in sections:
            if 'class' in section.attrs:
                if not 'en-rupture' in section.attrs['class']:
                    self.printnok("No out of stock found for %s" % section.text)
                    self.printnok("Link : %s" % list(section.absolute_links)[0])
                    self.outOfStock = False

        if self.outOfStock:
            self.printok('All is out of stock')
        else:
            # send an email
            self.sendEmail()

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
