# TonParse

Get price of transactions

## Description

1. Search tx-messages
2. Get full messages
3. Call getRate method
4. Calculate price
5. Save to JSON

## Installation

Instructions for installing the project.


1. Create venv
```bash
  python3 -m venv venv 
```
2. Activate the virtual environment

    (on Unix):
    ```bash 
      source venv/bin/activate
    ```
    (on Windows)
    ```bash 
      .\venv\Scripts\activate
    ```

3. Install requirements
```bash
  pip install -r requirements.txt
```

4. Create a .env file in the root of your project directory and add your environment variables:
   ```code
   CONTRACT_ADDRESS=''
   ABI_PATH=''
   SERVER_ADDRESS=''
   ```
   run: 
   ```bash
   source .env
   ```

5. Run
  ```bash 
    python start.py
  ```




