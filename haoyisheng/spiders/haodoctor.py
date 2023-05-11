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
        info = {}
        pattern = re.compile(r'(.*?):[\n\s]*(.*?)\((.*?)\)')
        department_name = response.meta['department_name']
        question_title = response.css('h1::text').extract_first()
        disease_info = response.css(".diseaseinfo *::text").extract()
        disease = "".join(disease_info).strip()
        results = pattern.findall(disease)
        for category, content, date in results:
            if category not in info:
                info[category] = content
            else:
                if category == '疾病描述':
                    if '疾病描述' not in info:
                        info['疾病描述'] = []
                    info['疾病描述'].append(content)
                else:
                    info[category] += ';' + content
        suggestions = response.css(".suggestions.marginLeft0 *::text").extract()
        suggestion = "".join(suggestions).strip()
