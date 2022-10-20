from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
import primer
import filemanager
from resource import resource_path
from subprocess import CREATE_NO_WINDOW

PATH = "./driver/chromedriver.exe"
NCBI_URL = "https://www.ncbi.nlm.nih.gov/nucleotide"
DESIGN_TOOL = "https://www.ncbi.nlm.nih.gov/tools/primer-blast/"


class Designer:

    def __init__(self, data: list):
        """Initializes designer, it utilizes chromedriver, opening of Chrome browser is prohibited by default."""
        options = webdriver.ChromeOptions()
        options.add_argument('--window-size=1920,1080')
        # options.add_argument('--headless')
        options.add_argument('--start-maximized')
        service = Service(resource_path(PATH))
        # service.creationflags = CREATE_NO_WINDOW
        self.driver = webdriver.Chrome(service=service, options=options)
        self.data = data
        self.nm_codes = None
        self.forward = None
        self.reverse = None
        self.max_length = 0
        self.fw_from = 1
        self.rw_to = 1
        self.over_intron = True
        self.attempts = 0

    def find_gene(self, elem: dict):
        """Tries to find the gene in the NCBI database"""
        self.driver.get(NCBI_URL)
        time.sleep(2)

        entry_element = self.driver.find_element(By.XPATH, '//*[@id="term"]')
        entry_element.send_keys(elem["gene"], " ", elem["organism"])
        time.sleep(1)

        search_element = self.driver.find_element(By.XPATH, '//*[@id="search"]')
        search_element.click()
        time.sleep(3)

        # Figures out the amount of transcript variants
        result = False
        try:
            transcript_element = self.driver.find_element(By.XPATH, '//*[@id="ui-sensor_content-7"]/p/a[2]')
            num = transcript_element.text.split(' ')[1]
            if num == "(1)":
                transcript_element.click()
                time.sleep(2)
                nm_code = self.driver.find_element(By.XPATH, '//*[@id="maincontent"]/div/div[5]/div[1]/p[1]').text
                nm_code = nm_code.split(":")[1].lstrip()
                self.nm_codes = [str(nm_code)]
                length = self.driver.find_element(By.XPATH, '//*[@id="viewercontent1"]/div/div/pre').text
                length = length.split(" bp")[0].split()[2]
                self.max_length = int(length)
            else:
                transcript_element.click()
                time.sleep(2)

                # Get NM code for every variant
                nms = self.driver.find_elements(By.CLASS_NAME, 'rprtid')
                self.nm_codes = [nm.text.split(': ')[1].split(' ')[0] for nm in nms
                           if nm.text.split(': ')[1].split(' ')[0][0:2] == 'NM']

                #Figures out the longest mRNAs with NM prefix
                mRNA_divs = self.driver.find_elements(By.CLASS_NAME, 'rslt')

                for mRNA in mRNA_divs:
                    if "Accession: NM" in mRNA.text:
                        length_elems = mRNA.find_elements(By.CLASS_NAME, "desc")
                        lengths = [int(length.text.split()[0].replace(",", "")) for length in length_elems]
                        self.max_length = max(lengths)
            self.rw_to = self.max_length
            result = True
        except NoSuchElementException:
            print("not found")
        finally:
            return result

    def design_primers(self, elem: dict):
        """When the gene has been found by 'find_gene', primers are designed by this method, it calls
        methods that set parameters and set properties of the primers to 'designer' instance."""
        if self.nm_codes:
            self.driver.get(DESIGN_TOOL)
            time.sleep(1)

            if len(self.nm_codes) > 1:
                mult_elem = self.driver.find_element(By.XPATH, '//*[@id="GroupTagrTab"]')
                mult_elem.click()
                time.sleep(1)

            item_id_area = self.driver.find_element(By.XPATH, '//*[@id="seq"]')

            for nm_code in self.nm_codes:
                item_id_area.send_keys(f'{nm_code}')
                item_id_area.send_keys(Keys.ENTER)

            self._set_prim_parameters(elem["organism"])
            self._set_adv_parameters()

            search = self.driver.find_element(By.XPATH, '//*[@id="srchBottom"]/div[1]/input')
            search.click()

            self._get_primers(elem)
        else:
            print("Gene has not been found.")

    def _set_prim_parameters(self, organism: str):
        """Sets the most important parameters (length, Tm, range, etc.)"""

        # Set range
        fw_from = self.driver.find_element(By.XPATH, '//*[@id="PRIMER5_START"]')
        fw_from.send_keys(self.fw_from)
        rw_to = self.driver.find_element(By.XPATH, '//*[@id="PRIMER3_END"]')
        rw_to.send_keys(f'{self.rw_to}')

        # Exclude predicted transcripts
        if len(self.nm_codes) > 1:
            exclude_box = self.driver.find_element(By.XPATH, '//*[@id="qseq"]/div[3]/label')
            exclude_box.click()
            exclude_ref_box = self.driver.find_element(By.XPATH, '//*[@id="excl"]/div/label[1]')
            exclude_ref_box.click()

        primer_prod_min = self.driver.find_element(By.XPATH, '//*[@id="PRIMER_PRODUCT_MIN"]')
        primer_prod_min.clear()
        primer_prod_min.send_keys(90)
        primer_prod_max = self.driver.find_element(By.XPATH, '//*[@id="PRIMER_PRODUCT_MAX"]')
        primer_prod_max.clear()
        primer_prod_max.send_keys(300)

        primer_opt_temp = self.driver.find_element(By.XPATH, '//*[@id="PRIMER_OPT_TM"]')
        primer_opt_temp.clear()
        primer_opt_temp.send_keys(61)

        tm_diff = self.driver.find_element(By.XPATH, '//*[@id="PRIMER_MAX_DIFF_TM"]')
        tm_diff.clear()
        tm_diff.send_keys(2)

        if self.over_intron:
            intron_incl = self.driver.find_element(By.XPATH, '//*[@id="query"]/fieldset[3]/div[4]')
            intron_incl.click()

        intron_min_size = self.driver.find_element(By.XPATH, '//*[@id="MIN_INTRON_SIZE"]')
        intron_min_size.clear()
        intron_min_size.send_keys(100)

        organism_entry = self.driver.find_element(By.XPATH, '//*[@id="ORGANISM"]')
        organism_entry.clear()
        organism_entry.send_keys(organism)

    def _set_adv_parameters(self):
        """Sets advanced parameters (salt concentration, amount of GC pairs) on the second tab."""
        adv_btn = self.driver.find_element(By.XPATH, '//*[@id="btnDescrOver"]')
        adv_btn.click()

        gc_min = self.driver.find_element(By.XPATH, '//*[@id="PRIMER_MIN_GC"]')
        gc_min.clear()
        gc_min.send_keys(40)

        gc_max = self.driver.find_element(By.XPATH, '//*[@id="PRIMER_MAX_GC"]')
        gc_max.clear()
        gc_max.send_keys(60)

        salt_conc = self.driver.find_element(By.XPATH, '//*[@id="CON_DNTPS"]')
        salt_conc.clear()
        salt_conc.send_keys(0.2)

    def _make_specific(self):
        """Adjusts ranges if there is problem to find specific primer."""
        eight_percent = self.max_length // 13
        if self.attempts > 6:
            self.rw_to -= eight_percent
            self.fw_from = 1
        else:
            self.fw_from += eight_percent

    def _get_primers(self, elem: dict):
        """It is responsible for setting the primer properties to the corresponding 'designer' instance attributes"""
        while True:
            try:
                specifity = self.driver.find_element(By.XPATH, '//*[@id="summary"]/div[1]/dl/dd[3]')
                if "Primer pairs are specific" == " ".join(specifity.text.split()[:4]):
                    forward_seq = self.driver.find_element(By.XPATH,
                                                           '//*[@id="alignments"]/div[1]/table/tbody/tr[2]/td[1]')
                    forward_len = self.driver.find_element(By.XPATH,
                                                           '//*[@id="alignments"]/div[1]/table/tbody/tr[2]/td[3]')
                    forward_tm = self.driver.find_element(By.XPATH,
                                                          '//*[@id="alignments"]/div[1]/table/tbody/tr[2]/td[6]')
                    reverse_seq = self.driver.find_element(By.XPATH,
                                                           '//*[@id="alignments"]/div[1]/table/tbody/tr[3]/td[1]')
                    reverse_len = self.driver.find_element(By.XPATH,
                                                           '//*[@id="alignments"]/div[1]/table/tbody/tr[3]/td[3]')
                    reverse_tm = self.driver.find_element(By.XPATH,
                                                          '//*[@id="alignments"]/div[1]/table/tbody/tr[3]/td[6]')
                    pcr_prod_len = self.driver.find_element(By.XPATH,
                                                            '//*[@id="alignments"]/div[1]/table/tbody/tr[5]/td')

                    self.forward = primer.Primer(elem["gene"], "F", forward_seq.text, forward_len.text, forward_tm.text,
                                                 pcr_prod_len.text,
                                                 elem["organism"])
                    self.reverse = primer.Primer(elem["gene"], "R", reverse_seq.text, reverse_len.text, reverse_tm.text,
                                                 pcr_prod_len.text,
                                                 elem["organism"])
                    self.attempts = 0
                    return
                else:
                    time.sleep(1)
                    self.over_intron = False
                    self.attempts += 1
                    self._make_specific()
                    self.design_primers(elem)
            except NoSuchElementException:
                try:
                    self.driver.find_element(By.CLASS_NAME, 'warning')
                    self.over_intron = False
                    self.design_primers(elem)
                except NoSuchElementException:
                    try:
                        submit = self.driver.find_element(By.XPATH, '//*[@id="userGuidedForm"]/div/div[1]/input')
                        submit.click()
                    except NoSuchElementException:
                        pass
                time.sleep(10)
                continue

    def print_primers(self):
        return f"{self.forward.print_primer()}\n{self.reverse.print_primer()}"

    def start_design(self):
        my_filemanager = filemanager.FileManager()
        for item in self.data:
            self.find_gene(item)
            self.design_primers(item)
            my_filemanager.export_to_xlsx(self.forward, self.reverse)

        self.driver.quit()


# my_designer = Designer("ppia", "homo sapiens")
