import scrapy
import re


class HaodoctorSpider(scrapy.Spider):
    name = 'haodoctor'
    allowed_domains = ['www.haodf.com']
    start_urls = ['https://www.haodf.com/bingcheng/list.html']

    def parse(self, response):
        # 解析首页，获取所有科室的url
        departments = response.css('.izixun-department span>a')
        for department in departments:
            department_url = department.css('::attr(href)').extract_first()
            if department_url.startswith('/'):
                department_url = 'https:' + department_url
            department_name = department.css('::text').extract_first()
            yield scrapy.Request(url=department_url, callback=self.parse_list, meta={'department_name': department_name})
            break

    def parse_list(self, response):
        # 解析科室经典问诊，获取所有页码的url
        department_name = response.meta['department_name']
        max_page_css = response.css('a.p_num::attr(href)').extract()
        if max_page_css:
            max_page_num = max_page_css[-1].split('=')[-1]
        else:
            max_page_num = 1
        for page_num in range(1, int(max_page_num) + 1):
            page_url = response.url + '?p=' + str(page_num)
            yield scrapy.Request(url=page_url, callback=self.parse_list_detail,
                                 meta={'department_name': department_name})
            break

    def parse_list_detail(self, response):
        # 解析每一页的问诊，获取所有问诊的url
        department_name = response.meta['department_name']
        questions = response.css('span.fl>a')
        for question in questions:
            question_url = question.css('::attr(href)').extract_first()
            yield scrapy.Request(url=question_url, callback=self.parse_detail,
                                 meta={'department_name': department_name})
            break
        pass

    def parse_detail(self, response):
        # 解析每个问诊的详情，获取所有回答的url
        # https://www.haodf.com/bingcheng/8892450147.html 该信息为患者隐私，无法查看
        err_msg = response.css('.error-msg::text').get()
        if err_msg:
            return
        info = {}
        pattern = re.compile(r'(.*?):[\n\s]*(.*?)\((.*?)\)')
        department_name = response.meta['department_name']
        question_title = response.css('h1::text').extract_first()
        disease_info = response.css(".diseaseinfo")
        disease_title = disease_info.css(".info3-title ::text").getall()
        disease_content1 = disease_info.css(".info3-value ::text").getall()
        disease_content2 = disease_info.css(".info3-title + .info3-value::text").getall()
        disease_content = []
        if len(disease_content1) != len(disease_content2):
            i = 0
            h = 0
            while len(disease_content2) != len(disease_content1):
                if disease_content2[i] == disease_content1[i]:
                    disease_content.append(disease_content2[i])
                    i = i + 1
                    h = i
                else:
                    if h == i:
                        h = h - 1
                    disease_content[h] = disease_content[h] + disease_content1[i]
                    del disease_content1[i]
                    if len(disease_content2) == len(disease_content1):
                        disease_content.append(disease_content2[i])
        disease = {}
        for i in range(len(disease_title)):
            disease[disease_title[i]] = disease_content[i]
        suggestions = response.css('.suggestions-text.paddingLeft20')
        suggestion = {}
        for sug in suggestions:
            suggestion_title = sug.css('curr-head-wrap *::text').getall()
            suggestion_title = "".join(suggestion_title).replace('\n', '').replace('\t', '').replace('\r', '')
            suggestion_content = sug.css('.suggestions-content *::text').getall()
            suggestion_content = "".join(suggestion_content).replace('\n', '').replace('\t', '').replace('\r', '').strip()
            suggestion[suggestion_title] = suggestion_content
        doctor_name = response.css(".info-text-name ::text").get()
        doctor_duties = response.css(".info-text-grade ::text").get()
        doctor_hospital = response.css(".info-text-faculty a *::text").getall()
        doctor_hospital = "".join(doctor_hospital).replace('\n', '').replace('\t', '').replace('\r', '').strip()
        doctor_good_at = response.css(".doctor-card-speciality div ::text").get().replace('\n', '').replace('\t', '').replace('\r', '').strip()
        # 患者投票以及在线问诊量
        doctor_count = response.css(".doctor-card-service .item-detail::text").getall()
        doctor_vote = doctor_count[0].replace('\n', '').replace('\t', '').replace('\r', '').strip()
        doctor_online = doctor_count[1].replace('\n', '').replace('\t', '').replace('\r', '').strip()
        info['disease'] = disease
        info['suggestion'] = suggestion
        info['department_name'] = department_name
        info['question_title'] = question_title
        doctor = {}
        doctor['doctor_name'] = doctor_name
        doctor['doctor_duties'] = doctor_duties
        doctor['doctor_hospital'] = doctor_hospital
        doctor['doctor_good_at'] = doctor_good_at
        doctor['doctor_vote'] = doctor_vote
        doctor['doctor_online'] = doctor_online
        info['doctor'] = doctor
        yield info
