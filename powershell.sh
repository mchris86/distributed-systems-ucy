# Create venv
# Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
python -m venv .venv
.venv\Scripts\Activate.ps1

pip install pyzmq

# Start client
Start-Process powershell -ArgumentList "python client.py"

# Start coordinator
Start-Process powershell -ArgumentList "python coordinator.py"

# Start participants
Start-Process powershell -ArgumentList "python participant.py 5556"
Start-Process powershell -ArgumentList "python participant.py 5557"
Start-Process powershell -ArgumentList "python participant.py 5558"