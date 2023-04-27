import matplotlib.pyplot as plt
import numpy as np
import random
from CSCS_agents import CSCSAgent, CompanyAgent

def plotting_result(Simulation):
    plt.subplot(331)
    plt.plot(Simulation.satellite_in_orbit)
    plt.title("Total satellite in orbit")

    plt.subplot(332)
    plt.plot(np.mean(Simulation.price,0),label = "Avg price")
    # plt.plot(Simulation.price[Simulation.num_companies+1,:],label = "CSCS price")
    plt.title("Price in market($/person/month)")

    plt.subplot(333)
    plt.plot(Simulation.adapting_percentage)
    plt.title("User adapting rate(%)")
    plt.ylim(0,100)

    plt.subplot(334)
    for i in range(5):
        plt.plot(Simulation.QOS[i,:])
    plt.title("QOS(Mb/person/s)")

    plt.subplot(335)
    plt.hist(Simulation.price_preference_profile, histtype = "step",label="original demand")
    plt.hist(Simulation.remaining_max_price_customer,label="unsatisfied demand")
    plt.title("Customer price preference profile")
    plt.xlabel("$/person/month")
    plt.ylabel("Thousand people")
    plt.legend()
    plt.ylim(0,2000)

    plt.subplot(336)
    plt.hist(Simulation.QOS_preference_profile, histtype = "step",label="original demand")
    plt.hist(Simulation.remaining_acceptable_QOS,label="unsatisfied demand")
    plt.title("Customer QOS preference profile")
    plt.legend()
    plt.xlabel("QOS(Mb)")
    plt.ylabel("Thousand people")
    plt.ylim(0,3500)

    plt.subplot(337)
    # for i in range(5):
    #     plt.plot(self.capital[i,:])
    plt.plot(np.sum(Simulation.capital[0:Simulation.num_companies-1],0),label = "Total capital")
    plt.ylim(100000,180000)
    # plt.plot(np.mean(Simulation.capital,0),label = "Avg capital")
    plt.legend()
    plt.title("Total capital in market(Million)")


    plt.subplot(338)
    for i in range(5):
        plt.plot(Simulation.CSCS_revenue_rate[i,:])
    plt.plot(np.mean(Simulation.CSCS_revenue_rate[0:Simulation.num_companies-1],0), label = "Avg CSCS revenue rate")
    plt.title("Revenue percentage from CSCS(%)")
    
    plt.subplot(339)
    # for i in range(5):
    #     plt.plot(Simulation.revenue[i,:])
    plt.plot(np.mean(Simulation.revenue[0:Simulation.num_companies-1],0),label = "Avg revenue")
    plt.plot(np.sum(Simulation.revenue[0:Simulation.num_companies-1],0),label = "Total revenue")

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
    if Simulation.num_CSCS == 0:
        plt.savefig("Result_no_CSCS.png")
    else:
        plt.savefig("Result_with_" + str(Simulation.num_CSCS) + "_CSCS.png")

    plt.show()

def init_logging_list(Simulation,num_steps):
    Simulation.num_steps = num_steps
    Simulation.satellite_in_orbit = np.zeros(num_steps)
    Simulation.adapting_percentage = np.zeros(num_steps)
    Simulation.remaining_max_price_customer = []
    Simulation.remaining_acceptable_QOS = []
    Simulation.total_capital = np.zeros(num_steps)
    Simulation.num_of_unsatisfied_price = np.zeros(num_steps)
    Simulation.num_of_unsatisfied_QOS = np.zeros(num_steps)
    Simulation.CSCS_revenue_rate = np.zeros((Simulation.num_companies+Simulation.num_CSCS,num_steps))
    Simulation.customers_count = np.zeros((Simulation.num_companies+Simulation.num_CSCS,num_steps))
    Simulation.capital = np.zeros((Simulation.num_companies+Simulation.num_CSCS,num_steps))
    Simulation.revenue = np.zeros((Simulation.num_companies+Simulation.num_CSCS,num_steps))
    Simulation.excess_capacity = np.zeros((Simulation.num_companies+Simulation.num_CSCS,num_steps))
    Simulation.price = np.zeros((Simulation.num_companies+Simulation.num_CSCS,num_steps))
    Simulation.QOS = np.zeros((Simulation.num_companies+Simulation.num_CSCS,num_steps))

def update_logging_list(Simulation,j,i,company):
    Simulation.price[j,i] = company.price*1000
    Simulation.QOS[j,i] = company.QOS if len(company.customers)>0 else 0
    Simulation.capital[j,i] = company.capital
    Simulation.total_capital[i] += company.capital
    Simulation.excess_capacity[j,i] = company.excess_capacity
    Simulation.revenue[j,i] = company.revenue_this_month
    Simulation.customers_count[j,i] = len(company.customers)
    Simulation.CSCS_revenue_rate[j,i] = company.CSCS_revenue_rate

def update_company(Simulation,i):

    for j, company in enumerate(Simulation.companies):
                    # print(j,company)
        if (i % 6) == 0:
            company.build_and_launch_sat()
        company.cal_QOS()
        company.cal_revenue_this_month()
        company.cal_new_capital()
        if company.Condition_to_join_CSCS(Simulation.num_companies,Simulation.num_CSCS) != None:
            company.Join_CSCS(company.Condition_to_join_CSCS(Simulation.num_companies,Simulation.num_CSCS),Simulation.companies)

        company.show_basic_info()
        if type(company) == CSCSAgent:
            # company.update_CSCS()
            company.show_CSCS_info()

        if type(company) == CompanyAgent:
            Simulation.satellite_in_orbit[i] += company.num_of_sat_on_orbit
        
        update_logging_list(Simulation, j,i,company)

def update_customer(Simulation,i):
    if (i % 6) == 0:
        for customer in Simulation.customers:
            customer.choose_company(Simulation.companies)
            customer.update_random_demand()
            for j, company in enumerate(Simulation.companies):
                company.cal_QOS()
            # customer.show_basic_info()

def cal_adapting_rate(Simulation,i):
    Simulation.remaining_max_price_customer = []
    Simulation.remaining_acceptable_QOS = []
    satisfied_demand_count = 0
    unusatisfied_demand_count = 0
    remaining_acceptable_price_sum = 0 
    # remaining_acceptable_QOS_sum = 0
    for customer in Simulation.customers:
        if customer.company == None:
            Simulation.remaining_max_price_customer.append(customer.max_acceptable_price*1000)
            Simulation.remaining_acceptable_QOS.append(customer.min_acceptable_QOS)
            unusatisfied_demand_count += 1
        else:
            satisfied_demand_count +=1
    remaining_avg_max_price_customer = remaining_acceptable_price_sum/unusatisfied_demand_count
    # remaining_avg_acceptable_QOS = remaining_acceptable_QOS_sum/unusatisfied_demand_count
    Simulation.adapting_percentage[i] = (1-unusatisfied_demand_count/Simulation.num_customers)*100

def update_company_price(Simulation,i):
    for j, company in enumerate(Simulation.companies):
        if (i % 6) == 0:
            company.update_price()