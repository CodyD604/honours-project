#include <stdlib.h>
#include <argp.h>
#include <pthread.h>
#include <unistd.h> // sleep

// Adapted from argp example #3
const char *argp_program_version = "";
const char *argp_program_bug_address = "";

static char doc[] = "A program for rapidly opening a file in read mode.";
static char args_doc[] = "";

/* The options we understand. */
static struct argp_option options[] = {
  {"single",   'l', 0,         0,  "Only read a single file, do not spawn threads that open repetitively"},
  {"file",     'f', "file",    0,  "File to open in read mode" },
  {"threads",  't', "threads", 0,  "Number of threads to open the file for"},
  {"seconds",  's', "seconds", 0,  "Amount of time in seconds to open the file"},
  { 0 }
};

/* Used by main to communicate with parse_opt. */
struct arguments
{
  int single, threads, secondsToRun;
  char *file;
};

/* Parse a single option. */
static error_t parse_opt (int key, char *arg, struct argp_state *state)
{
  /* Get the input argument from argp_parse, which we
     know is a pointer to our arguments structure. */
  struct arguments *arguments = state->input;

  switch (key)
    {
    case 'l':
      arguments->single = 1;
      break;
    case 't':
      arguments->threads = atoi(arg);
      break;
    case 'f':
      arguments->file = arg;
      break;
    case 's':
      arguments->secondsToRun = atoi(arg);
      break;

    default:
      return ARGP_ERR_UNKNOWN;
    }
  return 0;
}

// argp parser
static struct argp argp = { options, parse_opt, args_doc, doc };

// Open the file a given file. Close the file descriptor if for some reason we are able to get one.
int openFile(char* file_name)
{
   FILE *fp;
   fp = fopen(file_name, "r");

   if (fp != NULL) {
     fclose(fp);
   }

   return 0;
}

struct thread_data {
  char* file_name;
  int ret;
};

// Flag used to indicate that spawned threads should exit and we should collect their counts.
int quitFlag = 0;

// Function that our threads will run, rapidly opens a file and counts how many times this is done
// so long as the quit flag has not been set.
void *threadOp(void *threadArg)
{
  struct thread_data *args;
  args = (struct thread_data *) threadArg;
  int counter = 0;

  while (1)
  {
    if (quitFlag)
    {
      args->ret = counter;
      pthread_exit(NULL);
    }
    openFile(args->file_name);
    counter += 1;
  }

  pthread_exit(NULL);
}

int main(int argc, char *argv[])
{
  struct arguments arguments;
  char ch; 
  char* file_name;
  FILE *fp;

  // Arg defaults
  arguments.single = 0;
  arguments.threads = 1;
  arguments.file = "/home/cody/Desktop/myFile";
  arguments.secondsToRun = 30;

  // Parse arguments
  argp_parse (&argp, argc, argv, 0, 0, &arguments);

  pthread_t threads[arguments.threads];
  int* threadResults[arguments.threads];
  struct thread_data thread_data[arguments.threads];
  file_name = arguments.file;

  // File opening control.

  // Open the file once and exit.
  if (arguments.single)
  {
    openFile(file_name);
    return 0;
  }

  // Open the file repeatedly with 't' threads.
  // Based on https://hpc-tutorials.llnl.gov/posix/creating_and_terminating/
  int pthread_ret;
  for (int i=0; i < arguments.threads; i++)
  {
    thread_data[i].file_name = file_name;
    thread_data[i].ret = 0;
    pthread_ret = pthread_create(&threads[i], NULL, threadOp, (void *) &thread_data[i]);

    if (pthread_ret) {
      printf("ERROR; return code from pthread_create() is %d\n", pthread_ret);
      exit(-1);
    }
  }

  // Wait until we have opened the file for as long as the user wants to, then kill all threads.
  sleep(arguments.secondsToRun);
  quitFlag = 1;

  // Ensure threads have been terminated.
  for (int i=0; i < arguments.threads; i++)
  {
    pthread_join(threads[i], NULL);
  }

  // Count how many times we opened the file by summing the reported counts from each thread.
  int result = 0;
  for (int i=0; i < arguments.threads; i++)
  {
    result += thread_data[i].ret;
  }
  
  printf("Opened the file %d times in %d seconds.\n", result, arguments.secondsToRun);
  
  return 0;
}
