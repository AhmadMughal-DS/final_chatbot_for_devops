# DevOps Chatbot Deployment Guide

Welcome to the deployment guide for the DevOps Chatbot. Follow the steps below to deploy your application on an Ubuntu EC2 instance.

---

## Step 1: Launch an Ubuntu EC2 Instance

1. **Log in to AWS Console:**  
   Open the AWS Management Console and navigate to the EC2 service.
2. **Launch an Instance:**  
   - Click on **Launch Instances**.
   - Select an **Ubuntu Server (e.g., Ubuntu 22.04 LTS)** as the AMI.
   - Choose an instance type (e.g., `t2.micro`).
3. **Configure Security Group:**  
   Allow inbound traffic on port **22 (SSH)** and any other ports required.
4. **Launch & Key Pair:**  
   Launch the instance and download the associated SSH key pair.

*Once your Ubuntu EC2 instance is running, proceed to the next step.*

---

## Step 2: SSH into Your EC2 Instance and Clone Your Repository

1. **Open a Terminal on Your Local Machine.**
2. **SSH into Your Instance:**  
   Replace `mykey.pem` and the host with your actual key file and EC2 public DNS.
   ```bash
   chmod 400 mykey.pem
   ssh -i mykey.pem ubuntu@ec2-xx-xx-xx-xx.compute-1.amazonaws.com
   ```
3. **Update and Install Dependencies:**  
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   sudo apt-get install -y python3 python3-pip git
   ```
4. **Clone Your Repository:**  
   ```bash
   git clone https://github.com/AhmadMughal-DS/final_chatbot_for_devops
   ```

*After cloning, continue with the next steps.*

---

## Step 3: Set Up a Python Virtual Environment and Test Your App

1. **Navigate to Your Repository Folder:**  
   ```bash
   cd <YOUR_REPO_FOLDER>
   ```
2. **Create and Activate a Virtual Environment:**  
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install Dependencies:**
   - If using a `requirements.txt` file:
     ```bash
     pip install -r requirements.txt
     ```
   - Otherwise, install manually:
     ```bash
     pip install fastapi uvicorn
     ```
4. **Test-run Your App:**  
   Run the app on port 8000.
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```
5. **Verify in the Browser:**  
   Open your browser and navigate to `http://<EC2_PUBLIC_IP>:8000` to see your app running.

*Press Ctrl+C to stop the server after verification.*

---

## Step 4: Run the FastAPI App in the Background

1. **Run with nohup:**  
   While still in your project folder and with the virtual environment activated, run:
   ```bash
   nohup uvicorn main:app --host 0.0.0.0 --port 8000 &
   ```
   You should see a message like `[1] 12345` indicating the server is running in the background.
2. **Check Logs (Optional):**  
   To monitor log output:
   ```bash
   tail -f nohup.out
   ```

*Your application will keep running even if you disconnect from the SSH session.*

---

Follow these instructions to deploy your DevOps Chatbot successfully on an EC2 instance. For more information, refer to the AWS documentation or reach out for support.