# Two-Phase Commit (2PC) - Distributed Consensus Protocol  

This project implements the **Two-Phase Commit** distributed consensus protocol using the **ZeroMQ Dealer–Router model**.  
The system simulates how a coordinator ensures distributed agreement among multiple participants before committing or aborting a client transaction.

All components run inside a **continuous loop**, meaning new transactions begin automatically after each cycle.

---

## Overview

It ensures **atomicity** across multiple nodes:

> **Either all participants commit the transaction, or all abort**

This project implements:

- **1 Client**
- **1 Coordinator**
- **3 Participants**

Communication is fully asynchronous using ZeroMQ.

---

## Components

### **Client**
- Sends `TRANSACTION` to the coordinator  
- Waits for `COMMIT` or `ABORT`  
- Prints the result  
- Loops automatically to request a new transaction

---

### **Coordinator**
Runs a continuous loop implementing the 2PC algorithm:

#### **Phase 1: Prepare**
1. Wait for `TRANSACTION` from client  
2. Sleep 1–5 seconds (simulated processing)  
3. Broadcast `PREPARE` to all participants  
4. Wait for responses  

#### **Phase 2: Decision**
- If **all** participants reply `PREPARED`:  
  - Broadcast `COMMIT`  
  - Send `COMMIT` to client  

- If **any** participant replies `ABORT`:  
  - Broadcast `ABORT`  
  - Send `ABORT` to client  

The coordinator then loops and waits for the next client transaction.

---

### **Participants**
Each participant repeats forever:

- Upon receiving `PREPARE`:  
  - Randomly respond with `PREPARED` or `ABORT`  

- Upon receiving `COMMIT`:  
  - Respond with `ACK`  

- Upon receiving `ABORT`:  
  - Respond with `ACK`

Participants log each step to the terminal.

---

- **Client → DEALER → Coordinator ROUTER**  
- **Coordinator → DEALER → Participant ROUTER**

---

## Running the 2PC

```bash
  ./run.sh
```
