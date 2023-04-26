#Unit in million for all currency
import random
import numpy as np
import matplotlib.pyplot as plt

class CompanyAgent:
    def __init__(self, id, price=100, capital = 1000):
        self.id = id

    #Interaction between company and customer
        self.customers = []
        self.customers_id = []
        self.in_CSCS = False
        self.CSCS = None

    #Satellite technical model
        self.capacity_per_sat = 5000 #Mb/s
        self.num_of_sat_on_orbit = 0
        self.total_throughput = self.capacity_per_sat*self.num_of_sat_on_orbit
        self.throughput_per_custormer = 0
        self.QOS = 0
        self.total_demand = 0
        self.excess_capacity = 0
        self.target_sat_count = random.randint(100,1000)

    #Cost model
        self.price = price #price/1000 person/month
        self.capital = capital
        self.fixed_cost_each_month = 0
        self.recur_cost_this_month = 0 #fixed cost each month (operational cost)
        self.non_recur_cost = 7.5 #R&D cost 
        self.revenue_this_month = 0
        self.cost_per_sat = 0.75 #including launch
        
    def add_customer(self, customer):
        self.customers.append(customer)
        self.customers_id.append(customer.id)
        
    def remove_customer(self, customer):
        self.customers.remove(customer)
        self.customers_id.remove(customer.id)
        
    def update_price(self, remaining_avg_max_price_customer, customers):
        #To-do
        #Update this strategy
        if type(self) == CompanyAgent:
            self.total_demand = sum([c.demand for c in self.customers])
            self.excess_capacity = self.total_throughput - self.total_demand

            if self.price > remaining_avg_max_price_customer*1.2:
                self.price *= 0.95
            elif self.price < remaining_avg_max_price_customer*0.8:
                self.price *= 1.05

    def build_and_launch_sat(self):
        self.recur_cost_this_month = 0
        if self.capital > 600 and self.num_of_sat_on_orbit < self.target_sat_count and self.excess_capacity<10000:
            num_of_sat = random.randint(0,30)
            num_of_sat = self.capital/100/self.cost_per_sat
            self.num_of_sat_on_orbit += num_of_sat
            self.recur_cost_this_month += num_of_sat*self.cost_per_sat
        else:
            pass
            
        #To-do
        #Update this strategy

    def cal_new_capital(self):
        # print(self.revenue_this_month,self.recur_cost_this_month,self.fixed_cost_each_month)
        self.capital += self.revenue_this_month - self.recur_cost_this_month - self.fixed_cost_each_month
    
    def cal_revenue_this_month(self):
        if self.in_CSCS == True:
            self.CSCS_revenue = self.CSCS.revenue_this_month*self.num_of_sat_on_orbit/self.CSCS.num_of_sat_on_orbit
        else:
            self.CSCS_revenue = 0
        self.revenue_this_month = len(self.customers)*self.price + self.CSCS_revenue

    def cal_QOS(self):
        self.total_throughput = self.capacity_per_sat*self.num_of_sat_on_orbit
        self.throughput_per_custormer = self.total_throughput/max(len(self.customers),1) #Mb/1000people/s
        self.QOS = self.throughput_per_custormer/1000 #Mb/person/s

    def Condition_to_join_CSCS(self,num_of_company,num_of_CSCS):
        if num_of_CSCS==0:
            return None
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
                self.in_CSCS = True
                self.CSCS = CSCS
                print(CSCS.id)

    def show_basic_info(self):
        print("------------------------------------------------------------------------------")
        print("Company Id:",self.id)
        print("Agent type:", type(self))
        print("Customer count: ",len(self.customers_id))
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
        self.price = 0
        self.total_throughput = 0
        for company in self.comp_in_CSCS_list:
            self.price = (self.price*self.num_of_sat_on_orbit + company.price*company.num_of_sat_on_orbit)/(self.num_of_sat_on_orbit + company.num_of_sat_on_orbit)
            self.num_of_sat_on_orbit = self.num_of_sat_on_orbit + company.num_of_sat_on_orbit
            self.total_throughput = self.total_throughput+company.excess_capacity
        self.price = 1.5 * self.price

        self.throughput_per_custormer = self.total_throughput/max(len(self.customers),1)
        self.QOS = self.throughput_per_custormer/1000 #Mb/person/s
        self.revenue_this_month = len(self.customers)*self.price

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
            grade = a1*(self.max_acceptable_price - company.price)/self.max_acceptable_price + a2*(company.QOS-self.min_acceptable_QOS)/self.min_acceptable_QOS
            # print(grade)
            print(company.price < self.max_acceptable_price , company.QOS>self.min_acceptable_QOS, grade > current_grade)

            if company.price < self.max_acceptable_price  and company.QOS > self.min_acceptable_QOS: #only when it reach the minimum requirement
                updated_this_loop = True
                if grade > current_grade: #chose the highest grade
                    if self.company == None:
                        self.company = company
                        self.set_active()
                        current_grade = grade  
                    else:
                        self.set_inactive()
                        self.company = company
                        self.set_active()
                        current_grade = grade

            elif updated_this_loop == False:
                if self.company != None:
                    self.set_inactive()
                    self.company = None
                current_grade = 0

                # elif self.company != None:
                #     self.set_inactive()
                #     self.company = None
                #     current_grade = 0

    def update_random_demand(self): #demand of 1000 people in total
        self.demand = random.randint(self.min_acceptable_QOS-5,self.min_acceptable_QOS)*1000

    def show_basic_info(self):
        print("Customer",self.id,"Chosed company: ",self.company.id if self.company is not None else None)
        # print("Max_accepetable_price: ",self.max_acceptable_price)
        
class Simulation:
     #fixed number of CSCS, custormer and company. Note that some CSCS maybe empty, 
     #which means the num_CSCS is the max number of CSCS can formed in this system
    def __init__(self, num_companies, num_customers, num_CSCS):
        self.companies = []
        self.customers = []
        self.CSCS =[]
        self.num_companies = num_companies
        self.num_customers = num_customers
        self.num_CSCS = num_CSCS
        
        # Create companies
        for i in range(num_companies):
            price = random.randint(30, 120)# Dollar/person/month
            price = price/1000 #Convert to million per 1000 people
            capital = random.randint(1000, 10000) 
            company = CompanyAgent(i, price,capital)
            self.companies.append(company)
        
        # Create customers
        for i in range(num_customers):
            max_acceptable_price = random.randint(30, 120) #To-do set this profile
            max_acceptable_price = max_acceptable_price/1000 #Convert to million per 1000 people
            min_acceptable_QOS = random.randint(1,50)
            customer = CustomerAgent(i, max_acceptable_price, min_acceptable_QOS)
            self.customers.append(customer)
        
        for i in range(num_CSCS):
            CSCS = CSCSAgent(num_companies+i)
            self.companies.append(CSCS)
        
        # Assign customers to companies
        for customer in self.customers:
            customer.choose_company(self.companies)
            
    def run(self, num_steps):

        self.satellite_in_orbit = np.zeros(num_steps)
        self.adapting_percentage = np.zeros(num_steps)
        self.remaining_avg_max_price_customer = np.zeros(num_steps)
        self.remaining_avg_acceptable_QOS = np.zeros(num_steps)
        self.total_capital = np.zeros(num_steps)
        self.num_of_unsatisfied_price = np.zeros(num_steps)
        self.num_of_unsatisfied_QOS = np.zeros(num_steps)
        self.capital = np.zeros((self.num_companies+self.num_CSCS,num_steps))
        self.revenue = np.zeros((self.num_companies+self.num_CSCS,num_steps))
        self.excess_capacity = np.zeros((self.num_companies+self.num_CSCS,num_steps))
        self.price = np.zeros((self.num_companies+self.num_CSCS,num_steps))
        self.QOS = np.zeros((self.num_companies+self.num_CSCS,num_steps))

        print("*********************************************Begin Simulation***************************************************")
        
        for i in range(num_steps):
            print("Month ",i)

            # Update prices
            for j, company in enumerate(self.companies):
                # print(j,company)
                if (i % 6) == 0:
                    company.build_and_launch_sat()
                company.cal_QOS()
                company.cal_revenue_this_month()
                company.cal_new_capital()
                if company.Condition_to_join_CSCS(self.num_companies,self.num_CSCS) != None:
                    company.Join_CSCS(company.Condition_to_join_CSCS(self.num_companies,self.num_CSCS),self.companies)
                company.show_basic_info()
                if type(company) == CSCSAgent:
                    company.update_CSCS()
                    company.show_CSCS_info()
                self.price[j,i] = company.price*1000
                self.QOS[j,i] = company.QOS if len(company.customers)>0 else 0
                self.capital[j,i] = company.capital
                self.total_capital[i] += company.capital
                self.excess_capacity[j,i] = company.excess_capacity
                self.revenue[j,i] = company.revenue_this_month

                
            # customer switch company
            if (i % 6) == 0:
                for customer in self.customers:
                    # customer.choose_CSCS(self.CSCS)
                    customer.choose_company(self.companies)
                    customer.update_random_demand()
                    for j, company in enumerate(self.companies):
                        company.cal_QOS()
                    customer.show_basic_info()

            for company in self.companies:
                self.satellite_in_orbit[i] += company.num_of_sat_on_orbit

            satisfied_demand_count = 0
            unusatisfied_demand_count = 0
            remaining_acceptable_price_sum = 0 
            remaining_acceptable_QOS_sum = 0
            for customer in self.customers:
                if customer.company == None:
                    unusatisfied_demand_count+=1
                    remaining_acceptable_price_sum+=customer.max_acceptable_price
                    remaining_acceptable_QOS_sum+=customer.min_acceptable_QOS
                else:
                    satisfied_demand_count +=1
            remaining_avg_max_price_customer = remaining_acceptable_price_sum/unusatisfied_demand_count
            remaining_avg_acceptable_QOS = remaining_acceptable_QOS_sum/unusatisfied_demand_count
            self.remaining_avg_max_price_customer[i] = remaining_avg_max_price_customer*1000 
            self.remaining_avg_acceptable_QOS[i] = remaining_avg_acceptable_QOS
            self.adapting_percentage[i] = (1-unusatisfied_demand_count/self.num_customers)*100
            

            for j, company in enumerate(self.companies):
                if (i % 6) == 0:
                    company.update_price(remaining_avg_max_price_customer, self.adapting_percentage[i])
            print("****************************New Month********************************")

        print(np.mean(self.revenue[0:4,num_steps-1],0))
        print("adapting_percentage: ",self.adapting_percentage[num_steps-1])

        plt.subplot(331)
        plt.plot(self.satellite_in_orbit)
        plt.title("Total satellite in orbit")
        plt.subplot(332)
        plt.plot(self.capital[0,:])
        plt.plot(self.capital[1,:])
        plt.plot(self.capital[2,:])
        plt.plot(self.capital[3,:])
        plt.plot(self.capital[4,:])
        # plt.plot(self.total_capital)
        plt.title("Total capital in market")
        plt.subplot(333)
        # plt.plot(np.mean(self.price,0))
        plt.plot(self.price[0,:])
        plt.plot(self.price[1,:])
        plt.plot(self.price[2,:])
        plt.plot(self.price[3,:])
        plt.plot(self.price[4,:])
        plt.title("Price per person($/month) in market")
        plt.subplot(334)
        plt.plot(self.QOS[0,:])
        plt.plot(self.QOS[1,:])
        plt.plot(self.QOS[2,:])
        plt.plot(self.QOS[3,:])
        plt.plot(self.QOS[4,:])
        plt.title("QOS(Mb/person/s)")
        plt.subplot(335)
        plt.plot(self.adapting_percentage)
        plt.title("Adapting rate")
        plt.subplot(336)
        plt.plot(self.remaining_avg_max_price_customer)
        plt.title("remaining_avg_max_price_person($/month)")
        plt.subplot(337)
        plt.plot(self.remaining_avg_acceptable_QOS)
        plt.title("remaining_avg_acceptable_QOS")
        plt.subplot(338)
        plt.plot(self.excess_capacity[0,:])
        plt.plot(self.excess_capacity[1,:])
        plt.plot(self.excess_capacity[2,:])
        plt.plot(self.excess_capacity[3,:])
        plt.plot(self.excess_capacity[4,:])
        plt.title("Excess_capacity")
        plt.subplot(339)
        # plt.plot(self.revenue[0,:])
        # plt.plot(self.revenue[1,:])
        # plt.plot(self.revenue[2,:])
        # plt.plot(self.revenue[3,:])
        # plt.plot(self.revenue[4,:])
        plt.plot(np.mean(self.revenue[0:4,:],0))
        plt.title("Revenue this month")

        plt.show()

if __name__ == "__main__":
    Sim1 = Simulation(5,5000,2) #5000 for 
    #It is envisioned that the next generation of satellites (to be launched within the next 2-5 years) 
    #will bring down prices to $100/Mbps/month, which represents an estimated demand of 5 Tbps 
    #(currently the global satellite capacity for data networks is below 2 Tbps).
    Sim1.run(120) #10 years = 120

