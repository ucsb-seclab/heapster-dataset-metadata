/* SpwfInterface NetworkSocketAPI Example Program
 * Copyright (c) 2015 ARM Limited
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "mbed.h"
#include "SpwfInterface.h"
#include "TCPSocket.h"


#define BLINKING_RATE     500ms


// MAX 10 tasks 
unsigned int curr_taskID = 0;
unsigned int tasksCounter = 0;
unsigned int * tasks_array[10];

Serial pc(USBTX, USBRX);
DigitalOut myled(LED1);
SpwfSAInterface spwf(D8, D2, false);

DigitalOut led(LED1);

int NUM_TASK = 0;
unsigned int * tasks[10] = {};

int ADMIN_POWER = 0;

// Just some toy functionalities :)
void start_led(){
    if(!led) led = !led;
}

void stop_led(){
    if(led) led = !led;
}


int fill(char * input_data){

    // id from 0 to 9 
    input_data = input_data + 1;
    
    int task_id = *input_data - '0';
    
    if(task_id < 0 || task_id > 9){
      return 0;
    }
    if(tasks_array[task_id] == NULL){
      return 0;
    }
    
    unsigned int * curr_task = tasks_array[task_id];
    
    input_data = input_data + 1;
   
    unsigned int fill_size = (*(unsigned int *)input_data);
    
    pc.printf("[+] Filling chunk at 0x%08x with %d byte", curr_task, fill_size);
    
    input_data = input_data + 6;
    memcpy(curr_task, input_data, fill_size);     
}


void init_tasks_array(){
   for(int i=0; i<10;i++){
      tasks[i] = NULL;
   }    
}

// Just for debug
void print_heap(){
for(unsigned int k=0x20002310; k< 0x20002400; k+=4){
    pc.printf("[0x%08x] 0x%08x \n", k, *(unsigned int *)k);
    }
    
}

void do_something(){
    pc.printf("\r\n==============STARTING ACTIVITY [B]===============\n\n");
  //pc.printf("[!] Triggering fake free");
   // PLACE HERE AN ADDRESS YOU WANT TO ATTACK
   // WARNING: Sometimes memory fault can happen if hardware protects those
   // locations, this address should work. Further allocations are starting from
   // there.
  //free((unsigned int *)0x00002300); 
  
  free((unsigned int *)0x200001b0); 
  pc.printf("\r\n==============ENDED ACTIVITY [B]===============\n");
}



void do_activity(){
    // This is just a mock of a functionality affected by double-free.
    // For the sake of this demonstration we just trigger the vuln in 
    // a straight way as reported by Heapster.
    
    pc.printf("\r\n==============STARTING ACTIVITY [A]===============\n\n");
    
    unsigned int * a = (unsigned int *)malloc(8);
    pc.printf("[+]Malloc(8)\n");
    pc.printf("   -> Allocated chunk at 0x%08x\n", a);
    unsigned int * b = (unsigned int *)malloc(16);
    pc.printf("[+]Malloc(16)\n");
    pc.printf("   -> Allocated chunk at 0x%08x\n", b);
    
    pc.printf("[+]Free(0x%08x)\n", a);
    free(a);
    pc.printf("[+]Free(0x%08x)\n", b);
    free(b);
    unsigned int * c = (unsigned int *)malloc(32);
    pc.printf("[+]Malloc(32)\n");
    pc.printf("   -> Allocated chunk at 0x%08x\n", c);
    pc.printf("[+]Free(0x%08x)\n", b);
    free(b);
    
    unsigned int * d = (unsigned int *)malloc(8);
    pc.printf("[+]Malloc(8)\n");
    pc.printf("   -> Allocated chunk at 0x%08x\n", d);
    
    pc.printf("\r\n==============ENDED ACTIVITY [A]===============\n");
    
}


unsigned int * create_task(int size){
    if(NUM_TASK < 10){
        unsigned int * a = (unsigned int *)malloc(size);
        pc.printf("Task at 0x%08x\n",a);
        tasks[NUM_TASK] = a;
        memset(tasks[NUM_TASK], 0xFF, size);
        NUM_TASK++;
    }
}

unsigned int *fill_task(int task_id, int size, char *data){
    
    if(task_id < 0 || task_id > 9){
      return 0;
    }
    if(tasks[task_id] == NULL){
      return 0;
    }
    
    memcpy(tasks[task_id], data, size);
}


int delete_task(int task_id){
    if(task_id < 0 || task_id > 9){
      return 0;
    }
    if(tasks[task_id] == NULL){
      return 0;
    }
    
    pc.printf("Freeing task at 0x%08x", tasks[task_id]);
    free(tasks[task_id]);
    
    return 1;
}

/*
This firmware is meant to prove that heap exploitation is indeed possible 
when HML are not defending against exploitation primitives.
*/

void admin_console(){
  
  pc.printf("ADMIN VAR IS: %08x\n", ADMIN_POWER);
  
  if(ADMIN_POWER != 0){
      pc.printf("\nWELCOME ADMIN!!!!\n");
      }    
  else{
      pc.printf("\nYou are not admin!\n");
    }
}

void suicide(){
    if(ADMIN_POWER != 0){
       pc.printf("!!!!!!!!!!!!NUKE MODE ACTIVATED!!!!!!!!!!!!!");
       while(1){
        start_led();
        for(int i=0; i<1000;i++){
        }
        stop_led();
        for(int j=0; j<1000;j++){
        }
      }
    }else{
       pc.printf("ONLY ADMIN CAN SEND THIS COMMAND!\n");
    }
}


int main() {
    int err;    
    
    
    pc.printf("ADMIN_POWER: 0x%08x", &ADMIN_POWER);
    
    /*
    ===================================
    =============WARNING===============
    ===================================
    The current configuration of the board is to 
    connect to a 2.4GHZ AP with discoverable SSID and WPA2 AUTH.
    Devices MUST be on the same network.
    */
    char * ssid = "dd-wrt";  //ssid of the router where the IoT device is connecting
    char * seckey = "";  // passphrase of the router 
    
    char * neuromancer_ip = "192.168.1.135";  // ip of the machine that is sending commands (hosting the exploit)
    int neuromancer_port = 31337;   // port of the machine that is sending commands 
    
    pc.printf("\r\n========X-NUCLEO-IDW01M1 mbed Application========\r\n");
    
    pc.printf("\r\n==============ENABLING NETWORK===============\n");
    pc.printf("\r\n[+] Trying to connect to AP: [%s]\r\n", ssid);
    pc.printf("\r\n[+] Trying to connect using PASSPHRASE: [%s]\r\n", seckey);
            
    if(spwf.connect(ssid, seckey, NSAPI_SECURITY_WPA2)) {      
        pc.printf("\r\n[+] Now connected\r\n");
    } else {
        pc.printf("\r\n[!] Error connecting to AP.\r\n");
        return -1;
    }   

    const char *ip = spwf.get_ip_address();
    const char *mac = spwf.get_mac_address();
    
    pc.printf("\r\n[+] IP Address is: %s\r\n", (ip) ? ip : "No IP");
    pc.printf("\r\n[+] MAC Address is: %s\r\n", (mac) ? mac : "No MAC");    
    
    //SocketAddress addr(&spwf, "st.com");   
    //pc.printf("\r\nst.com resolved to: %s\r\n", addr.get_ip_address());    

    TCPSocket socket(&spwf);
    socket.bind(spwf.get_ip_address());

    pc.printf("\r\n[+] Connecting to {Neuromancer} server at %s:%d\r\n", neuromancer_ip, neuromancer_port);

    while(socket.connect(neuromancer_ip, neuromancer_port)){
        pc.printf("Cannot connect to {Neuromancer}. Retry.");
    }

    pc.printf("\r\n==============ENABLED NETWORK===============\n");

    char buffer[100];
    int count = 0;
    
    //init_tasks_array();
    
    
    
    while(1){

        pc.printf("\r\n[+]Waiting for input from the device\n"); 
        count = socket.recv(buffer, sizeof buffer);
        
        if(count > 0)
        {
            buffer [count]='\0';
            pc.printf("[+] COMMAND RECEIVED IS %c\r\n", buffer[0]);  
        }
        
        if ( buffer[0] == '1')
            start_led();
        
        if(buffer[0] == '2')
            stop_led();
            
        if(buffer[0] == '3'){
              //pc.printf("Starting activity!");
              do_activity();
            }
        if(buffer[0] == '4'){
            do_something();
            }
        if(buffer[0] == '5'){
            unsigned int * a = (unsigned int *)malloc(10);
            pc.printf("\r\n[+] Allocated chunk at 0x%08x\n", a);
            }

        if(buffer[0] == '6'){
              char * input_data = buffer + 1;
              int task_size = (*(int *)input_data);
              pc.printf("Size of task %d", task_size);
              create_task(task_size);
            }
            
        if(buffer[0] == '7'){
              char * input_data = buffer + 1;
              int task_size = (*(int *)input_data);
              input_data = buffer + 5;
              int task_id = (*(char *)input_data);
              input_data = buffer + 6;
              fill_task(task_id,task_size, input_data);
            }
        if(buffer[0] == '8'){
               print_heap();
            }
        if(buffer[0] == '9'){
               char * input_data = buffer + 1;
               int task_id = (*(char *)input_data);
               delete_task(task_id);
            }
        if(buffer[0] == 'a'){
               char * input_data = buffer + 1;
               int task_id = (*(char *)input_data);
               delete_task(task_id);
            }
        if(buffer[0] == 'c'){
               admin_console();
            }

        if(buffer[0] == 'e'){
               suicide();
            }
    }
    
    
    pc.printf("\r\n[+] Closing Socket\r\n");
    //socket.close();
    pc.printf("\r\n[+]  Unsecure Socket Test complete.\r\n");
    printf ("[+]  Socket closed\n\r");
    spwf.disconnect();
    printf ("[+]  WIFI disconnected, exiting ...\n\r");

}
