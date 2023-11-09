## 🚀 Bring localhost to Internet!

This platform provides you to bring the localhost server to the internet (only RESTful servers)

### Initial Thoughts
- This project is created to entirely demonstrate the usecases of blockchain and the smart contracts and their usecases over testnets.  
- This is **not** meant to be a real-time communication mechanism or any means.  
- This is suitable for triggering some actions remotely in periodic way, where communication delay is not a concern.  
- As per testing, with some 1 test ETH, we can have almost 200 round trips of communication.  

### What you need?
- Metamask account
- Test ether

### How to Deploy?
- get the entire repository for the frontend client whoever is going to access remotely
- Just get the directory named "bakend server" to the actual server deployed on localhost

Suppose lets say you have two machines behind NAT, where establishing connection between them requires relying on third party servers which will handle your data by relaying it.
Rather than that, whatever service you are hosting on your server, simply let it run on localhost.  

---

### Setting up backend
Lets say you have two machines, A and B,
You are running a service on B, run it on localhost with some port suppose 8000,   
Then get our backend server as discussed above, deploy the contract, and simply get the contract address and paste it in the .env file, and then,  
run it as,  
```
python3 server.py
```
--- 

### Setting up frontend

Run frontend django server on frontend whoever is going to access the service, simply copy and paste the contract address and run it as,

```
python3 manage.py runserver 8000
```
---

Now, simply query requests, and wait for around 15 seconds to get the reply!






