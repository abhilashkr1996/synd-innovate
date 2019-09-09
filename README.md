### What's this application is about?
It's basically a real time queue management system for banks. 

### What are it's features?
- Dashboard for the branch manager for live monitoring of the traffic
- Dashboard for the client to perform request udpate
- Mobile Application for the users for booking an appointment (UI to be completed)
- Report Generation at the end of the day

### What's the application stack we have used for this project?
- Firebase for user authentication
- Firestore as database
- Python for application server
- HTML, CSS and Javascript for Front End
- Redis as caching server

### How to run the app locally?

Setting up Manually:
	1. First and foremost install anaconda from [https://www.anaconda.com/distribution/](https://www.anaconda.com/distribution/)
	2. Create a new environment with python=3
	3. Activate the environment
	4. Go to the project folder
	5. Run the following command  - `pip install -r requirements.txt`
	6. If you get any errors during the running of the above command, please revert back to me @ abhilash.khokle@gmail.com
	7. Once everything is set up, run the following command - `python main.py`
	8. If everything runs smoothly, go the browser and plug in `http://localhost:5000`
	

**We will soon give you a docker image that  automates the manual installation**

Points to keep note:	
- Login Interface for Admin and Clerk is same
- As of now there are 2 branches we have. One is "123" and other one is "SYNB0009004"
- The admins of the following branches are as follows:
	- branch - 123
		- admin email - india@gmail.com
		- admin password - indian
	- branch - SYNB0009004
		- admin email - shankar@gmail.com
		- admin password - indian


##### Login as admin:
- Once you are logged in successfully you can see live traffic for the present day. 
- Admin functions include 
	- add a clerk
	- remove a clerk
	- add a counter
	- he can also see how the system behaves with different amount of resources (according to queuing theory)

In the admin counter section, you can see all the counters. You can add a counter but not delete one. Instead each counter will have Time to live feature which helps to delete the counter automatically. 

In the admin section you can add a clerk but you need to add the counter name also to which the clerk belongs. Hence, give a valid counter name.

##### Login as clerk:
- Once you login as clerk, depending on the counter assigned to you and the time of the day (where the slot_id is inferred from) requests are shown to you.
- When you create the counters, you will be giving slots for each counters.
- If the same slot time is not the real time (current time at the moment you login) then it's not the application's fault
- Once you see requests, then you can see the timer running off.
- Once you click "done" button, the next request in the queue appears.

**Very Important Note**:
- Only I can add a new branch. Please revert back to me for creation of new branch and the admin for that branch
- When this application is handed over to the Syndicate Bank, the database admin team will take care of creating new branches and adding their respective admins
- For every branch you create, there needs to atleast a counter and a clerk assigned to the branch. We don't consider an empty branch to be existent. This is the job of the database admin to add atleast one counter and a clerk to the branch 


Contact US:
1. Phone number: 9538917727
2. email - abhilash.khokle@gmail.com