# SWMR ABD Distributed Protocol Implementation with ZeroMQ

## Overview

This project implements the **Single-Writer Multiple-Reader (SWMR) ABD protocol**, a distributed algorithm that emulates a fault-tolerant shared memory in an asynchronous system.

The ABD protocol provides **strong consistency** using:

- Active replication  
- Logical timestamps  
- Majority quorums (n/2 + 1)  
- Asynchronous communication  

Communication is implemented using **ZeroMQ** with the **DEALER–ROUTER** pattern, which naturally supports asynchronous request/reply messaging between clients (writer/readers) and servers.

---

## Protocol Details

### Writer Protocol

**Initialization**

- `msg_id = 0`  
- `ts = 0`

**WRITE(val)**

1. `ts = ts + 1`  
2. `msg_id = msg_id + 1`  
3. Broadcast to all servers:  
   `<write, msg_id, val, ts>`  
4. Wait for:  
   `<write_ack, msg_id>`  
   from a **majority of servers** (n/2 + 1)

---

### Reader Protocol

**Initialization**

- `msg_id = 0`  
- `val = -1`  
- `ts = 0`

**READ()**

1. `msg_id = msg_id + 1`  
2. Broadcast to all servers:  
   `<query, msg_id>`  
3. Wait for:  
   `<query_ack, msg_id, v', ts'>`  
   from a **majority** of servers  
4. Let `(v_max, ts_max)` be the pair with the **maximum timestamp** among the replies  
5. `msg_id = msg_id + 1`  
6. Broadcast to all servers:  
   `<inform, msg_id, v_max, ts_max>`  
7. Wait for:  
   `<inform_ack, msg_id>`  
   from a **majority** of servers

The write-back (`inform`) step ensures that all future reads will observe at least the timestamp `ts_max`, preserving atomic (linearizable) semantics.

---

### Server Protocol

**Initialization**

- `val = 0`  
- `ts = 0`

**On `<write, msg_id, v, max_ts>`**

1. Set `ts = max_ts` and `val = v`  
2. Wait a random delay between 1 and 5 seconds  
3. Send `<write_ack, msg_id>` back to the writer

**On `<query, msg_id>`**

1. Wait a random delay between 1 and 5 seconds  
2. Send `<query_ack, msg_id, val, ts>` back to the reader

**On `<inform, msg_id, v, max_ts>`**

1. If `max_ts > ts`, then set:
   - `ts = max_ts`  
   - `val = v`  
2. Wait a random delay between 1 and 5 seconds  
3. Send `<inform_ack, msg_id>` back to the reader

---

## ZeroMQ Model

- **Writer / Readers**
  - Use **DEALER** sockets to connect to all servers.
  - Can send and receive asynchronously.
- **Servers**
  - Use **ROUTER** sockets.
  - Receive identity frames from clients and reply using the same envelope.
  - Handle messages from multiple writers/readers (here: one writer, multiple readers).

This follows the Dealer–Router model required by the lab instructions.

---

## Running the System

```bash
  ./run.sh
```