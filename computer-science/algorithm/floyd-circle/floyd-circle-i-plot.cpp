//floyd-circle-i-plot.cpp - 这个程序测试了Floyd算法的不同变体在不同链表配置下的性能，并将结果保存到CSV文件中以供后续分析和绘图。
#include <iostream>
#include <vector>
#include <chrono>
#include <fstream>
#include <string>

using namespace std;
using namespace std::chrono;

struct ListNode {
    int val;
    ListNode *next;
    char padding[128]; // 模拟重型对象，放大 Cache Miss 影响
    ListNode(int x) : val(x), next(nullptr) {}
};

// 制作环逻辑
ListNode* createList(int n, int entry) {
    if (n <= 0) return nullptr;
    vector<ListNode*> nodes;
    for (int i = 0; i < n; i++) nodes.push_back(new ListNode(i));
    for (int i = 0; i < n - 1; i++) nodes[i]->next = nodes[i + 1];
    if (entry >= 0 && entry < n) nodes[n - 1]->next = nodes[entry];
    return nodes[0];
}

void freeList(ListNode* head, int n, int entry) {
    if (!head) return;
    if (entry >= 0) {
        ListNode* cur = head;
        for (int i = 0; i < n - 1; i++) cur = cur->next;
        cur->next = nullptr;
    }
    while (head) {
        ListNode* nxt = head->next;
        delete head;
        head = nxt;
    }
}

// 核心测试逻辑
long long runFloyd(ListNode* head, int k) {
    if (!head) return 0;
    ListNode *slow = head, *fast = head;
    long long count = 0;
    while (true) {
        for (int i = 0; i < k; i++) {
            if (!slow || !slow->next) return count;
            slow = slow->next; count++;
        }
        for (int i = 0; i < 2 * k; i++) {
            if (!fast || !fast->next) return count;
            fast = fast->next; count++;
        }
        if (slow == fast) return count;
    }
}

int main() {
    system("chcp 65001 > nul");
    ofstream csv("floyd_raw_data.csv");
    csv << "TotalSize,CycleType,CyclePos,StepK,AvgTime,AccessCount\n";

    // 要求的 5 种链表长度
    vector<int> sizes = {1000, 5000, 10000, 50000, 100000};
    vector<int> k_list;
    for(int i=1; i<=20; i++) k_list.push_back(i);
    for(int v : {32, 64, 128, 256}) k_list.push_back(v);

    for (int N : sizes) {
        vector<pair<string, int>> scenarios = {
            {"NoCycle", -1}, {"Small(1%)", (int)(N*0.99)}, 
            {"Mod(30%)", (int)(N*0.7)}, {"Mod(60%)", (int)(N*0.4)}, 
            {"Large(90%)", (int)(N*0.1)}
        };

        for (auto& sc : scenarios) {
            cout << "Running - Size: " << N << ", Scenario: " << sc.first << endl;
            for (int k : k_list) {
                ListNode* head = createList(N, sc.second);
                
                auto t1 = high_resolution_clock::now();
                int iters = (N > 10000) ? 50 : 500; 
                for(int i=0; i<iters; i++) runFloyd(head, k);
                auto t2 = high_resolution_clock::now();
                
                long long accessCount = runFloyd(head, k);
                double avgTime = duration_cast<nanoseconds>(t2 - t1).count() / (double)iters / 1000000.0;
                
                csv << N << "," << sc.first << "," << sc.second << "," << k << "," << avgTime << "," << accessCount << "\n";
                freeList(head, N, sc.second);
            }
        }
    }
    csv.close();
    return 0;
}