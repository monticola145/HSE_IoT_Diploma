uint16_t    LUM_result;                                
uint8_t     PIN_illumination = A0;                     
 
void setup() { 
  Serial.begin(9600);                                  
 
  } 
void loop() { 
  LUM_result = 1024 - analogRead(PIN_illumination);                     
  Serial.println(LUM_result);                          
}
