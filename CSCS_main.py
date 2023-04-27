#Unit in million for all currency
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
        self.fixed_cost_each_month = 0
        self.recur_cost_this_month = 0 #fixed cost each month (operational cost)
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
        
    def update_price(self, remaining_avg_max_price_customer, customers):
        # To-solve problem
        # If all the company implement the same startegy, they tend to reach similar price and QOS, 
        # which resulting in competing for the same group of customer.
        # Need to find a way to assign different price strategy for different company
        if type(self) == CompanyAgent or CSCSAgent:
            self.total_demand = sum([c.demand for c in self.customers])
            self.excess_capacity = self.total_throughput - self.total_demand

            if self.price > remaining_avg_max_price_customer*0.8 or len(self.customers)< self.max_customer_count:
                self.price *= 0.9
            elif self.price < remaining_avg_max_price_customer*1.2 or len(self.customers) >= self.max_customer_count:
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
        
class Simulation:
     #fixed number of CSCS, custormer and company. Note that some CSCS maybe empty, 
     #which means the num_CSCS is the max number of CSCS can formed in this system
    def __init__(self, num_companies, num_customers, num_CSCS):
        self.companies = []
        self.customers = []
        self.price_preference_profile = []
        self.QOS_preference_profile = []
        self.num_companies = num_companies
        self.num_customers = num_customers
        self.num_CSCS = num_CSCS
        
        # Create companies
        for i in range(num_companies):
            price = random.randint(100, 200)# Dollar/person/month
            price = price/1000 #Convert to million per 1000 people
            capital = random.randint(1000, 10000) 
            company = CompanyAgent(i, price,capital)
            self.companies.append(company)
        
        # Create customers
        for i in range(num_customers):
            min_price = 20
            max_price = 150
            scale_parameter = 0.5
            max_acceptable_price = powerlaw.rvs(scale_parameter, 0)*max_price + min_price
            self.price_preference_profile.append(max_acceptable_price)
            max_acceptable_price = max_acceptable_price/1000 #Convert to million per 1000 people

            min_QOS = 20
            max_QOS = 300
            scale_parameter = 0.2
            min_acceptable_QOS = powerlaw.rvs(scale_parameter, 0)*max_QOS + min_QOS
            self.QOS_preference_profile.append(min_acceptable_QOS)

            customer = CustomerAgent(i, max_acceptable_price,min_acceptable_QOS)

            # max_acceptable_price = random.randint(30, 150) #To-do set this profile
            # max_acceptable_price = max_acceptable_price/1000 #Convert to million per 1000 people
            
            customer = CustomerAgent(i, max_acceptable_price, min_acceptable_QOS)
            self.customers.append(customer)
        
        for i in range(num_CSCS):
            CSCS = CSCSAgent(num_companies+i)
            self.companies.append(CSCS) #save CSCS in list of company
        
        # Assign customers to companies
        for customer in self.customers:
            customer.choose_company(self.companies)
            
    def run(self, num_steps):

        self.satellite_in_orbit = np.zeros(num_steps)
        self.adapting_percentage = np.zeros(num_steps)
        self.remaining_max_price_customer = []
        self.remaining_acceptable_QOS = []
        self.total_capital = np.zeros(num_steps)
        self.num_of_unsatisfied_price = np.zeros(num_steps)
        self.num_of_unsatisfied_QOS = np.zeros(num_steps)
        self.CSCS_revenue_rate = np.zeros((self.num_companies+self.num_CSCS,num_steps))
        self.customers_count = np.zeros((self.num_companies+self.num_CSCS,num_steps))
        self.capital = np.zeros((self.num_companies+self.num_CSCS,num_steps))
        self.revenue = np.zeros((self.num_companies+self.num_CSCS,num_steps))
        self.excess_capacity = np.zeros((self.num_companies+self.num_CSCS,num_steps))
        self.price = np.zeros((self.num_companies+self.num_CSCS,num_steps))
        self.QOS = np.zeros((self.num_companies+self.num_CSCS,num_steps))

        print("*********************************************Begin Simulation***************************************************")
         
        for i in range(num_steps):
            self.remaining_max_price_customer = []
            self.remaining_acceptable_QOS = []

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
                    # company.update_CSCS()
                    company.show_CSCS_info()
                self.price[j,i] = company.price*1000
                self.QOS[j,i] = company.QOS if len(company.customers)>0 else 0
                self.capital[j,i] = company.capital
                self.total_capital[i] += company.capital
                self.excess_capacity[j,i] = company.excess_capacity
                self.revenue[j,i] = company.revenue_this_month
                self.customers_count[j,i] = len(company.customers)
                self.CSCS_revenue_rate[j,i] = company.CSCS_revenue_rate

                
            # customer switch company
            if (i % 6) == 0:
                for customer in self.customers:
                    # customer.choose_CSCS(self.CSCS)
                    customer.choose_company(self.companies)
                    customer.update_random_demand()
                    for j, company in enumerate(self.companies):
                        company.cal_QOS()
                    # customer.show_basic_info()

            for company in self.companies:
                if type(company) == CompanyAgent:
                    self.satellite_in_orbit[i] += company.num_of_sat_on_orbit

            satisfied_demand_count = 0
            unusatisfied_demand_count = 0
            remaining_acceptable_price_sum = 0 
            # remaining_acceptable_QOS_sum = 0
            for customer in self.customers:
                if customer.company == None:
                    self.remaining_max_price_customer.append(customer.max_acceptable_price*1000)
                    self.remaining_acceptable_QOS.append(customer.min_acceptable_QOS)
                    unusatisfied_demand_count += 1
                else:
                    satisfied_demand_count +=1
            remaining_avg_max_price_customer = remaining_acceptable_price_sum/unusatisfied_demand_count
            # remaining_avg_acceptable_QOS = remaining_acceptable_QOS_sum/unusatisfied_demand_count
            self.adapting_percentage[i] = (1-unusatisfied_demand_count/self.num_customers)*100
            

            for j, company in enumerate(self.companies):
                if (i % 6) == 0:
                    company.update_price(remaining_avg_max_price_customer, self.adapting_percentage[i])
            print("****************************New Month********************************")

        # print("Total Revenue: ",np.sum(self.revenue[0:4,num_steps-1],0))
        print("adapting_percentage: ",self.adapting_percentage[num_steps-1])

        plt.subplot(331)
        plt.plot(self.satellite_in_orbit)
        plt.title("Total satellite in orbit")

        plt.subplot(332)
        plt.plot(np.mean(self.price,0),label = "Avg price")
        # plt.plot(self.price[self.num_companies+1,:],label = "CSCS price")
        plt.title("Price in market($/person/month)")

        plt.subplot(333)
        plt.plot(self.adapting_percentage)
        plt.title("User adapting rate(%)")
        plt.ylim(0,100)

        plt.subplot(334)
        for i in range(5):
            plt.plot(self.QOS[i,:])
        plt.title("QOS(Mb/person/s)")

        plt.subplot(335)
        plt.hist(self.price_preference_profile, histtype = "step",label="original demand")
        plt.hist(self.remaining_max_price_customer,label="unsatisfied demand")
        plt.title("Customer price preference profile")
        plt.xlabel("$/person/month")
        plt.ylabel("Thousand people")
        plt.legend()
        plt.ylim(0,2000)

        plt.subplot(336)
        plt.hist(self.QOS_preference_profile, histtype = "step",label="original demand")
        plt.hist(self.remaining_acceptable_QOS,label="unsatisfied demand")
        plt.title("Customer QOS preference profile")
        plt.legend()
        plt.xlabel("QOS(Mb)")
        plt.ylabel("Thousand people")
        plt.ylim(0,3500)

        plt.subplot(337)
        # for i in range(5):
        #     plt.plot(self.capital[i,:])
        plt.plot(np.sum(self.capital[0:self.num_companies-1],0),label = "Total capital")
        plt.ylim(100000,180000)
        # plt.plot(np.mean(self.capital,0),label = "Avg capital")
        plt.legend()
        plt.title("Total capital in market(Million)")


        plt.subplot(338)
        for i in range(5):
            plt.plot(self.CSCS_revenue_rate[i,:])
        plt.plot(np.mean(self.CSCS_revenue_rate[0:self.num_companies-1],0), label = "Avg CSCS revenue rate")
        plt.title("Revenue percentage from CSCS(%)")
        
        plt.subplot(339)
        # for i in range(5):
        #     plt.plot(self.revenue[i,:])
        plt.plot(np.mean(self.revenue[0:self.num_companies-1],0),label = "Avg revenue")
        plt.plot(np.sum(self.revenue[0:self.num_companies-1],0),label = "Total revenue")

        plt.legend()
        plt.title("Revenue per month(Million)")


        plt.subplots_adjust(left=0.1,
                    bottom=0.1,
                    right=0.9,
                    top=0.9,
                    wspace=0.4,
                    hspace=0.4)
        mng = plt.get_current_fig_manager()
        mng.full_screen_toggle()
        if self.num_CSCS == 0:
            plt.savefig("Result_no_CSCS.png")
        else:
            plt.savefig("Result_with_" + str(self.num_CSCS) + "_CSCS.png")

        plt.show()

        return (np.sum(self.revenue[0:self.num_companies-1,num_steps-1],0), self.adapting_percentage[num_steps-1])

if __name__ == "__main__":
    #5000 for
    #It is envisioned that the next generation of satellites (to be launched within the next 2-5 years) 
    #will bring down prices to $100/Mbps/month, which represents an estimated demand of 5 Tbps 
    #(currently the global satellite capacity for data networks is below 2 Tbps).
    log  = False
    if log == True:
        trial = 20
        revenue_log = np.zeros((2,trial))
        adapting_rate_log = np.zeros((2,trial))
        for i in range(trial):
            Sim1 = Simulation(30,5000,0) 
            (revenue_log[0,i],adapting_rate_log[0,i]) =  Sim1.run(120) #10 years = 120
            Sim2 = Simulation(30,5000,2)
            (revenue_log[1,i],adapting_rate_log[1,i]) = Sim2.run(120)
        np.savetxt("revenue.csv",revenue_log,delimiter=",")
        np.savetxt("adpating_rate.csv",adapting_rate_log,delimiter=",")
        print(revenue_log)
        print(adapting_rate_log)
    else:
        Sim1 = Simulation(30,5000,0) 
        Sim1.run(240)

    

