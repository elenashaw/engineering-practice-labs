**Problem from**: Modern Operating System(by Andrew Tanenbaum) chapter 2: 65

**Problem Statement:**   Implement a program to count the frequency of words in a text file. The text file is partitioned into N segments. Each segment is processed by a separate thread that out puts the intermediate frequency count for its segment. The main process waits until all the threads complete; then it computes the consolidated word-frequency data based on the individual threads’ output

**Problem Analysis:**
1.Segmentation Strategy
    
- Assumptions: Assuming a stochastic distribution of word lengths, we can partition the text based on fixed byte offsets (alphabet length). This avoids the $O(n)$ computational overhead of pre-scanning the file to count total words, significantly improving initialization speed.


- Method: The text is divided into $N$ equal-sized segments by character count. To preserve word integrity, a boundary alignment (fine-tuning) mechanism is applied: each segment boundary is shifted to the nearest whitespace to ensure that no word is truncated between two threads.

- Programming Details:
    - input: file path
    - output: index of starts and ends.
    


2. Thread behaviors and their data strutures
    1. Thread Communication Strategy
        - Constraint: In Python (and most OS models), a Thread object cannot directly "return" a value like a standard function.

        - Solution: Use a Shared Container (e.g., a List) initialized by the main process. Each thread is assigned a specific index (slot) in the list to store its final result.

    2. Choice of Data Structure
        - Local Storage: Each thread maintains its own dictionary (Hash Map) to store local word frequencies: {word: count}.

        - Global Aggregation: After all threads finish (join), the main process merges these individual dictionaries into a final one.

    3. Concurrency Model: Why "Split-and-Merge"?
        The Problem with Global Sharing: If all threads update a single global dictionary, we face:

        - Race Conditions: Non-atomic updates (read-modify-write) can lead to lost counts.

        - Synchronization Overhead: To prevent data corruption, we would need Locks (Mutexes). Frequent locking/unlocking turns parallel execution into serial execution, killing performance.

        The Advantage of Local Dictionaries: This makes the task Embarrassingly Parallel. Threads work in their own "memory silos" without interference, maximizing CPU throughput and bypassing GIL-related bottlenecks during the counting phase.

    4. The Counting Logic (Worker Function)
        - Text Processing:

            - Segmentation: Use .decode().split() to handle whitespace and convert bytes to strings.

            - Boundary Handling: Since get_segments aligns boundaries at spaces, we avoid splitting a single word between two threads.

        - Dictionary Maintenance (Python):
            ```python
                    # Optimization of your if-else logic:
                    if word in local_dic:
                        local_dic[word] += 1
                    else:
                        local_dic[word] = 1

                    # Or even more concisely:
                    # local_dic[word] = local_dic.get(word, 0) + 1
            ```
