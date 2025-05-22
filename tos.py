#!/usr/bin/env python3
"""
TOS - Turnaround-Optimized Scheduler
COMP3100/6105 Assignment 2
"""

import socket
import sys
import time
import signal

class TOScheduler:
    def __init__(self, timeout=300):
        self.username = sys.argv[1] if len(sys.argv) > 1 else "default_user"
        self.timeout = timeout
        
        self.socket = None
        self.host = 'localhost'
        self.port = 50000

        self.servers_info = {}
        self.total_jobs = 0
        self.completed_jobs = 0
        self.start_time = time.time()
        
        # job packing
        self.enable_job_packing = True
        self.max_server_load = 0.8
        self.utilization_bonus = 50
        self.waiting_job_penalty = 120
        self.running_job_penalty = 30
        self.boot_time_penalty = 60
        
        self.small_job_threshold = 2
        self.medium_job_threshold = 4
        
    def connect_to_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        print(f"Connected to {self.host}:{self.port}")
        return True
    
    def write_message(self, message):
        print(f"Sending: {message}")
        self.socket.send(message.encode())
        
    def read_message(self):
        response = self.socket.recv(1024).decode()
        print(f"Received: {response}")
        return response.strip()
    
    def get_servers(self, cores, memory, disk):
        self.write_message(f"GETS Capable {cores} {memory} {disk}")
        
        response = self.read_message()
        if not response.startswith("DATA"):
            return []
            
        parts = response.split()
        num_records = int(parts[1])
        
        self.write_message("OK")
        
        server_data = ""
        while len(server_data) < 10000:
            chunk = self.socket.recv(4096).decode()
            server_data += chunk
            if len(chunk) < 4096:
                break
        
        servers = []
        
        lines = server_data.split('\n')
        for line in lines:
            if not line.strip() or line.strip() == ".":
                continue
                
            parts = line.split()
            if len(parts) >= 7:
                server_info = {
                    'type': parts[0], 
                    'id': parts[1],
                    'state': parts[2],
                    'start_time': parts[3],
                    'cores': int(parts[4]),
                    'memory': int(parts[5]),
                    'disk': int(parts[6]),
                    'waiting_jobs': int(parts[7]) if len(parts) > 7 else 0,
                    'running_jobs': int(parts[8]) if len(parts) > 8 else 0,
                    'available_cores': int(parts[4]), 
                    'available_memory': int(parts[5]),
                    'available_disk': int(parts[6]),
                    'load_factor': 0.0
                }
                
                self.update_server_load(server_info)
                
                server_key = f"{server_info['type']}_{server_info['id']}"
                self.servers_info[server_key] = server_info
                
                servers.append(server_info)
        
        self.write_message("OK")
        self.read_message()
        
        return servers
    
    def update_server_load(self, server):
        if server['cores'] > 0:
            core_util = (server['cores'] - server['available_cores']) / server['cores']
            memory_util = (server['memory'] - server['available_memory']) / server['memory']
            disk_util = (server['disk'] - server['available_disk']) / server['disk']
            
            server['load_factor'] = 0.6 * core_util + 0.3 * memory_util + 0.1 * disk_util
        else:
            server['load_factor'] = 0.0
    
    def classify_job(self, cores, memory, disk):
        cores = int(cores)
        
        if cores <= self.small_job_threshold:
            return "small"
        elif cores <= self.medium_job_threshold:
            return "medium"
        else:
            return "large"
    
    def classify_server(self, server):
        cores = server['cores']
        if cores <= 2:
            return "small"
        elif cores <= 8:
            return "medium"
        else:
            return "large"
    
    def estimate_wait_time(self, server, current_time):
        if server['state'] == 'inactive':
            return self.boot_time_penalty
        elif server['state'] == 'booting':
            start_time = int(server['start_time'])
            remaining_boot_time = max(0, self.boot_time_penalty - (current_time - start_time))
            return remaining_boot_time
        else:
            return 0
    
    def can_run_job(self, server, cores, memory, disk):
        return (server['available_cores'] >= int(cores) and 
                server['available_memory'] >= int(memory) and 
                server['available_disk'] >= int(disk))
    
    def select_best_server(self, servers, cores, memory, disk, current_time):
        if not servers:
            return None

        cores = int(cores)
        memory = int(memory)
        disk = int(disk)
        
        job_size = self.classify_job(cores, memory, disk)
        
        best_server = None
        best_score = float('inf')
        
        active_servers = [s for s in servers if s['state'] == 'active' and self.can_run_job(s, cores, memory, disk)]
    
        for server in servers:
            if not self.can_run_job(server, cores, memory, disk):
                continue
            score = 0
            
            wait_time = self.estimate_wait_time(server, current_time)
            score += wait_time
            
            score += server['waiting_jobs'] * self.waiting_job_penalty

            score += server['running_jobs'] * self.running_job_penalty

            if self.enable_job_packing:
                server_size = self.classify_server(server)
                if server['load_factor'] > 0.3 and server['load_factor'] < self.max_server_load:
                    if server['state'] == 'active':
                        if (job_size == "small" and server_size == "small") or \
                           (job_size == "medium" and server_size == "medium") or \
                           (job_size == "large" and server_size == "large"):
                            score -= self.utilization_bonus * 1.5
                        else:
                            score -= self.utilization_bonus
                
                if job_size == "small" and server_size == "large":
                    score += 50
            
            if score < best_score:
                best_score = score
                best_server = server
        
        return best_server
    
    def update_server_resources(self, server_key, cores, memory, disk, operation="decrease"):
        if server_key not in self.servers_info:
            return
            
        server = self.servers_info[server_key]
        
        multiplier = -1 if operation == "decrease" else 1
        
        server['available_cores'] += multiplier * int(cores)
        server['available_memory'] += multiplier * int(memory)
        server['available_disk'] += multiplier * int(disk)
        
        if operation == "increase":
            server['available_cores'] = min(server['available_cores'], server['cores'])
            server['available_memory'] = min(server['available_memory'], server['memory'])
            server['available_disk'] = min(server['available_disk'], server['disk'])
            
            self.update_server_load(server)
    
    def run(self):
        if not self.connect_to_server():
            return
            
        self.write_message("HELO")
        response = self.read_message()
        
        if response != "OK":
            print(f"Handshake failed: {response}")
            return
            
        self.write_message(f"AUTH {self.username}")
        response = self.read_message()
        
        if response != "OK":
            print(f"Authentication failed: {response}")
            return
            
        self.write_message("REDY")
        
        scheduled_jobs = {}
        
        while True:
            response = self.read_message()
            
            if response == "NONE":
                break
                
            if response.startswith("JOBN") or response.startswith("JOBP"):
                parts = response.split()
                
                if len(parts) >= 7:
                    # JOBN/JOBP jobID submitTime cores memory disk estRuntime
                    job_id = parts[1]
                    submit_time = int(parts[2])
                    cores = parts[3]
                    memory = parts[4]
                    disk = parts[5]
                    est_runtime = parts[6]
                    
                    job_info = {
                        'id': job_id,
                        'submit_time': submit_time,
                        'cores': cores,
                        'memory': memory,
                        'disk': disk,
                        'est_runtime': est_runtime
                    }
                    
                    servers = self.get_servers(cores, memory, disk)
                    
                    if servers:
                        best_server = self.select_best_server(servers, cores, memory, disk, submit_time)
                        
                        if best_server:
                            self.write_message(f"SCHD {job_id} {best_server['type']} {best_server['id']}")
                            response = self.read_message()
                            
                            if response == "OK":
                                self.total_jobs += 1
                                
                                server_key = f"{best_server['type']}_{best_server['id']}"
                                self.update_server_resources(server_key, cores, memory, disk, "decrease")
                                
                                if best_server['state'] == 'active':
                                    best_server['running_jobs'] += 1
                                else:
                                    best_server['waiting_jobs'] += 1
                                
                                scheduled_jobs[job_id] = {
                                    'job': job_info,
                                    'server': server_key,
                                    'scheduled_time': submit_time
                                }
                            else:
                                print(f"ERROR: Failed to schedule job {job_id} - {response}")
                
            elif response.startswith("JCPL"):
                parts = response.split()
                if len(parts) >= 5:
                    completion_time = parts[1]
                    job_id = parts[2]
                    server_type = parts[3]
                    server_id = parts[4]
                    
                    server_key = f"{server_type}_{server_id}"
                    
                    if job_id in scheduled_jobs:
                        job_info = scheduled_jobs[job_id]['job']
                        self.update_server_resources(server_key, job_info['cores'], 
                                                    job_info['memory'], job_info['disk'], "increase")
                        
                        if server_key in self.servers_info:
                            self.servers_info[server_key]['running_jobs'] -= 1
                    
                    self.completed_jobs += 1
                    print(f"Job {job_id} completed on {server_type} {server_id} at time {completion_time}")
            
            self.write_message("REDY")
        
        signal.alarm(0)
        
        self.write_message("QUIT")
        response = self.read_message()
        self.socket.close()
        
        elapsed = time.time() - self.start_time
        
        print(f"\n=== Scheduling completed ===")
        print(f"Total jobs scheduled: {self.total_jobs}")
        print(f"Completed jobs: {self.completed_jobs}")
        print(f"Elapsed time: {elapsed:.1f} seconds")

if __name__ == "__main__":
    timeout = 300
    if len(sys.argv) > 2 and sys.argv[2].isdigit():
        timeout = int(sys.argv[2])
        
    scheduler = TOScheduler(timeout=timeout)
    scheduler.run()