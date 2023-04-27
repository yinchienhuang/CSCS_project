import random
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import powerlaw

class CompanyAgent:
    def __init__(self, id, price=100, capital = 1000):
        self.id = id

    #Interaction between company and customer
        self.customers = []
        self.intended_QOS = random.randint(2,80)
        self.max_customer_count = 0
        self.customers_id = []
        self.in_CSCS = False
        self.CSCS = None

    #Satellite technical model
        self.capacity_per_sat = 8000 #Mb/s
        self.num_of_sat_on_orbit = 0
        self.total_throughput = self.capacity_per_sat*self.num_of_sat_on_orbit
        self.throughput_per_custormer = 0
        self.QOS = 0
        self.total_demand = 0
        self.excess_capacity = 0
        self.target_sat_count = 1000

    #Cost model
        self.price = price #price/1000 person/month
        self.capital = capital
        self.fixed_cost_each_month = 0 #fixed cost each month (operational cost)
        self.recur_cost_this_month = 0 
        self.non_recur_cost = 7.5 #R&D cost 
        self.revenue_this_month = 0
        self.revenue_without_CSCS = 0
        self.CSCS_revenue_rate = 0
        self.cost_per_sat = 0.75 #including launch
        
    def add_customer(self, customer):
        self.customers.append(customer)
        self.customers_id.append(customer.id)
        
    def remove_customer(self, customer):
        self.customers.remove(customer)
        self.customers_id.remove(customer.id)
        
    def update_price(self):
        # To-solve problem
        # If all the company implement the same startegy, they tend to reach similar price and QOS, 
        # which resulting in competing for the same group of customer.
        # Need to find a way to assign different price strategy for different company
        if type(self) == CompanyAgent or CSCSAgent:
            self.total_demand = sum([c.demand for c in self.customers])
            self.excess_capacity = self.total_throughput - self.total_demand

            if len(self.customers)< self.max_customer_count: #self.price > remaining_avg_max_price_customer*0.8 or 
                self.price *= 0.9
            elif len(self.customers) >= self.max_customer_count: #self.price < remaining_avg_max_price_customer*1.2 or 
                self.price *= 1.1
            self.price += self.intended_QOS*0.2/1000

    def build_and_launch_sat(self):
        self.recur_cost_this_month = 0
        #some condition for the company to launch more satellite. Will need to adjust the strategy in the future
        #target_sat_count is a ramdon number initialized as a "plan" for this company
        if self.capital > 600 and self.num_of_sat_on_orbit < self.target_sat_count: # and self.excess_capacity<10000
            num_of_sat = random.randint(0,30)
            num_of_sat = round(self.capital/100/self.cost_per_sat)
            self.num_of_sat_on_orbit += num_of_sat
            self.recur_cost_this_month += num_of_sat*self.cost_per_sat
            self.max_customer_count = self.total_throughput/self.intended_QOS/1000
        else:
            pass
            
        #To-do
        #Update this strategy

    def cal_new_capital(self):
        # print(self.revenue_this_month,self.recur_cost_this_month,self.fixed_cost_each_month)
        self.capital += self.revenue_this_month - self.recur_cost_this_month - self.fixed_cost_each_month
        self.target_sat_count = self.capital/10
        
    def cal_revenue_this_month(self):
        if self.in_CSCS == True:
            self.CSCS_revenue = self.CSCS.revenue_this_month*self.num_of_sat_on_orbit/self.CSCS.num_of_sat_on_orbit
        else:
            self.CSCS_revenue = 0

        self.revenue_without_CSCS = len(self.customers)*self.price
        self.revenue_this_month = self.revenue_without_CSCS  + self.CSCS_revenue
        if self.revenue_this_month != 0:
            self.CSCS_revenue_rate = self.CSCS_revenue/self.revenue_this_month*100

    def cal_QOS(self):
        self.total_throughput = self.capacity_per_sat*self.num_of_sat_on_orbit
        self.throughput_per_custormer = self.total_throughput/max(len(self.customers),1) #Mb/1000people/s
        self.QOS = self.throughput_per_custormer/1000 #Mb/person/s

    def Condition_to_join_CSCS(self,num_of_company,num_of_CSCS):
        if num_of_CSCS==0:
            return None
        # Join a random CSCS right now, should have some more condition, such as expected revenue
        target_CSCS_id = random.randint(num_of_company,num_of_company+num_of_CSCS-1)
        if type(self) == CompanyAgent and self.in_CSCS == False:
            if self.capital<10000 and self.excess_capacity > 10000:
                # print(target_CSCS_id)
                return target_CSCS_id
        else:
            return None

    def Join_CSCS(self, target_CSCS_id, all_CSCS):
        for CSCS in all_CSCS:
            if (CSCS.id == target_CSCS_id) and (self not in CSCS.comp_in_CSCS_list):
                CSCS.comp_in_CSCS_list.append(self)
                CSCS.update_CSCS()
                self.in_CSCS = True
                self.CSCS = CSCS
                print(CSCS.id)

    def show_basic_info(self):
        print("------------------------------------------------------------------------------")
        print("Company Id:",self.id)
        print("Agent type:", type(self))
        print("Customer count: ",len(self.customers_id))
        print("Max customer count: ",self.max_customer_count)
        # print("Customer list: ", self.customers_id)
        # print("Price(million/1000people/month): ",self.price)
        print("Price per person($):", self.price/1000*1000000)
        print("Revenue from CSCS: ", self.CSCS_revenue)
        print("Revenue this month(Million): ",self.revenue_this_month)
        print("Current Capital(Million): ",self.capital)
        print("Target satellite count:", self.target_sat_count)
        print("Orbiting satellite count: ",round(self.num_of_sat_on_orbit))

        print("Total throughput(Mb):", self.total_throughput)
        # print("Throughput per customer (Mb/1000 people/s)", self.throughput_per_custormer)
        print("Total demand from customers(Mb): ", self.total_demand)
        print("Quality of service(Mb/person/s): ",self.QOS)
        print("excess_capacity for comapny "+ str(self.id)+ "(Mb):",self.excess_capacity)
        print("------------------------------------------------------------------------------")

class CSCSAgent(CompanyAgent): #Join CSCS, cost remain but has extra throughput
    def __init__(self, id, price=0, capital=0):
        super().__init__(id, price, capital)
        self.comp_in_CSCS_list = []

    def update_CSCS(self):
        self.num_of_sat_on_orbit = 0
        self.ini_price = 0
        self.total_throughput = 0
        for company in self.comp_in_CSCS_list:
            self.ini_price = (self.price*self.num_of_sat_on_orbit + company.price*company.num_of_sat_on_orbit)/(self.num_of_sat_on_orbit + company.num_of_sat_on_orbit)
            self.num_of_sat_on_orbit = self.num_of_sat_on_orbit + company.num_of_sat_on_orbit
            self.total_throughput = self.total_throughput+company.excess_capacity
        # self.price = 0.2 * self.price

        self.throughput_per_custormer = self.total_throughput/max(len(self.customers),1)
        self.QOS = self.throughput_per_custormer/1000 #Mb/person/s
        self.revenue_this_month = len(self.customers)*self.price
        # self.max_customer_count = 80
        self.intended_QOS = 10
        self.max_customer_count = self.total_throughput/self.intended_QOS/1000
        self.price = self.ini_price

    def show_CSCS_info(self):
        id_list = []
        for company in self.comp_in_CSCS_list:
            id_list.append(company.id)
        print("Company in this CSCS:", id_list)

class CustomerAgent: #a agent represent 1000 peopel
    def __init__(self, id, max_acceptable_price, min_acceptable_QOS):
        self.id = id
        self.demand = 0 # Mb/s/1000 people
        self.max_acceptable_price = max_acceptable_price # Randomly generate this to simulate the customer profile, as Fig.10-5
        self.min_acceptable_QOS = min_acceptable_QOS
        self.active = False
        self.company = None #The sat company this customer choose
        
    def set_active(self):
        # Activate the customer
        self.active = True
        self.company.add_customer(self)
        
    def set_inactive(self):
        # Deactivate the customer
        self.active = False
        self.company.remove_customer(self)
    #The strategy is to choose the company that can provide maximum bitrate with acceptable price
    def choose_company(self, companies):
        a1 = 0.5 #propotion of price concern
        a2 = 0.5 #propotion of QOS concern
        current_grade = 0
        updated_this_loop = False
        for company in companies:
            # grade = a1*(normolized price difference) + a2 * (normalized QOS difference)
            grade = a1*(self.max_acceptable_price - company.price)/self.max_acceptable_price + a2*(company.QOS-self.min_acceptable_QOS)/company.QOS
            # print(grade)
            # print(company.price < self.max_acceptable_price , company.QOS>self.min_acceptable_QOS, grade > current_grade, len(company.customers)<company.max_customer_count)
            # and company.QOS > self.min_acceptable_QOS 
            if company.price < self.max_acceptable_price and len(company.customers)<company.max_customer_count: #only when it reach the minimum requirement
                if grade > current_grade: #chose the highest grade
                    updated_this_loop = True
                    if self.company == None:
                        self.company = company
                        self.set_active()
                        current_grade = grade  
                    else:
                        self.set_inactive()
                        self.company = company
                        self.set_active()
                        current_grade = grade
            elif updated_this_loop == False: #If there is no company achieve the requirement, set company to None
                if self.company != None:
                    self.set_inactive()
                    self.company = None
                current_grade = 0

    def update_random_demand(self): #demand of 1000 people in total
        self.demand = random.randint(round(self.min_acceptable_QOS-5),round(self.min_acceptable_QOS))*1000

    def show_basic_info(self):
        print("Customer",self.id,"Chosed company: ",self.company.id if self.company is not None else None)
        # print("Max_accepetable_price: ",self.max_acceptable_price)
        