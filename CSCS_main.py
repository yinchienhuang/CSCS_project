#Unit in million for all currency
import random
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import powerlaw
import util
from CSCS_agents import CompanyAgent, CSCSAgent, CustomerAgent
     
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

        util.init_logging_list(self,num_steps)

        print("*********************************************Begin Simulation***************************************************")
         
        for i in range(num_steps):
            print("Month ",i)
            util.update_company(self,i)
            util.update_customer(self,i)
            util.cal_adapting_rate(self,i)
            util.update_company_price(self,i)
            print("****************************New Month********************************")

        print("Total Revenue: ",np.sum(self.revenue[0:self.num_companies-1,num_steps-1],0))
        print("adapting_percentage: ",self.adapting_percentage[num_steps-1])

        util.plotting_result(self)

        return (np.sum(self.revenue[0:self.num_companies-1,num_steps-1],0), self.adapting_percentage[num_steps-1])


if __name__ == "__main__":
    Sim1 = Simulation(30,5000,5) 
    Sim1.run(240)
    #5000 for
    #It is envisioned that the next generation of satellites (to be launched within the next 2-5 years) 
    #will bring down prices to $100/Mbps/month, which represents an estimated demand of 5 Tbps 
    #(currently the global satellite capacity for data networks is below 2 Tbps).
    # log  = False
    # if log == True:
    #     trial = 20
    #     revenue_log = np.zeros((2,trial))
    #     adapting_rate_log = np.zeros((2,trial))
    #     for i in range(trial):
    #         Sim1 = Simulation(30,5000,0) 
    #         (revenue_log[0,i],adapting_rate_log[0,i]) =  Sim1.run(120) #10 years = 120
    #         Sim2 = Simulation(30,5000,2)
    #         (revenue_log[1,i],adapting_rate_log[1,i]) = Sim2.run(120)
    #     np.savetxt("revenue.csv",revenue_log,delimiter=",")
    #     np.savetxt("adpating_rate.csv",adapting_rate_log,delimiter=",")
    #     print(revenue_log)
    #     print(adapting_rate_log)
    # else:
    

    

