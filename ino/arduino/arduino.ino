#include "FastLED.h"
#define SW_PIN      A6
#define LED_PIN     3
#define NUM_LEDS    8
CRGB leds[NUM_LEDS];

#define BUFFER_SIZE 50
char buffer[BUFFER_SIZE + 1];  // +1 for null terminator


void setup() {
  Serial.begin(9600);
  FastLED.addLeds<WS2812, LED_PIN, GRB>(leds, NUM_LEDS);
  pinMode(SW_PIN, 2);

}

int sw_status = 1;
int old_sw_status = 1;

void loop() {
  while (1) {
    if (Serial.available()) {
      // Read new character from Serial
      char ch = Serial.read();
      char str[2] = {ch, '\0'};
      addToBuffer(str);
      if (ch == '>') {
        break;
      }
    }
    main_();
  }
  check_command();
}

void check_command() {
  char* command = extractCommand(buffer);
  //Serial.println("!!!!!!!!!!!!");
  //Serial.println(buffer);
  //Serial.println(command);

  char* splitResult[10];  // Assuming max 10 parts
  int splitSize;
  splitCommand(command, splitResult, &splitSize);

  if (strcmp(splitResult[0], "crgb") == 0) {
    int r = atoi(splitResult[1]);
    int g = atoi(splitResult[2]);
    int b = atoi(splitResult[3]);
    for (int i = 0; i < 8; i++)
      leds[i] = CRGB(r, g, b);
    FastLED.show();

  }

  // Free allocated memory for splitResult
  for (int i = 0; i < splitSize; i++) {
    free(splitResult[i]);
  }
  free(command);  // Free the allocated memory for command

}

void main_() {

  old_sw_status = sw_status;
  sw_status = digitalRead(SW_PIN);

  // กด
  if (sw_status == 0 && old_sw_status == 1) {
    for (int i = 0; i < 8; i++)
      leds[i] = CRGB(100, 100, 100);
    FastLED.show();
    Serial.print("<press>");
  }

  // ปล่อย
  else if (sw_status == 1 && old_sw_status == 0) {
    for (int i = 0; i < 8; i++)
      leds[i] = CRGB(10, 10, 10);
    FastLED.show();
    Serial.print("<release>");
  }
}




void addToBuffer(const char* input) {
  char cleanedInput[strlen(input) + 1];
  int j = 0;

  // Remove '\n' and '\r' characters
  for (int i = 0; input[i] != '\0'; i++) {
    if (input[i] != '\n' && input[i] != '\r') {
      cleanedInput[j++] = input[i];
    }
  }
  cleanedInput[j] = '\0';

  int cleanedLength = strlen(cleanedInput);
  int bufferLength = strlen(buffer);

  if (cleanedLength >= BUFFER_SIZE) {
    // If the new string is longer than or equal to the buffer size,
    // copy the last BUFFER_SIZE characters
    strncpy(buffer, cleanedInput + (cleanedLength - BUFFER_SIZE), BUFFER_SIZE);
  }
  else if (bufferLength + cleanedLength > BUFFER_SIZE) {
    // If adding the new string would exceed the buffer size,
    // shift the existing content and append the new string
    int shift = bufferLength + cleanedLength - BUFFER_SIZE;
    memmove(buffer, buffer + shift, bufferLength - shift);
    strncpy(buffer + (BUFFER_SIZE - cleanedLength), cleanedInput, cleanedLength);
  }
  else {
    // If there's enough space, simply append the new string
    strcat(buffer, cleanedInput);
  }

  buffer[BUFFER_SIZE] = '\0';  // Ensure null termination
}

char* extractCommand(const char* input) {
  int length = strlen(input);
  if (input[length - 1] != '>') {
    return NULL;
  }
  const char* start = strrchr(input, '<');
  if (start < input + length - 1) {
    int commandLength = input + length - 1 - start - 1;
    char* command = (char*)malloc(commandLength + 1);
    strncpy(command, start + 1, commandLength);
    command[commandLength] = '\0';
    return command;
  }
  return NULL;
}

void splitCommand(const char* command, char** result, int* resultSize) {
  char temp[strlen(command) + 1];
  strcpy(temp, command);

  *resultSize = 0;
  char* token = strtok(temp, "(,)");
  while (token != NULL && *resultSize < 10) {  // Limit to 10 parts to avoid overflow
    result[*resultSize] = (char*)malloc(strlen(token) + 1);
    strcpy(result[*resultSize], token);
    (*resultSize)++;
    token = strtok(NULL, "(,)");
  }
}
