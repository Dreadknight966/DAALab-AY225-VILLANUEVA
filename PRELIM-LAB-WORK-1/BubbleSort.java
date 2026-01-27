import java.io.*;
import java.util.*;

public class BubbleSort {

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        // Ask user for file path
        System.out.print("Enter the path of the dataset text file: ");
        String filePath = sc.nextLine();

        File file = new File(filePath);
        if (!file.exists()) {
            System.out.println("File does not exist. Exiting...");
            return;
        }

        // Read numbers from the file
        List<Integer> numbersList = new ArrayList<>();
        try (Scanner fileScanner = new Scanner(file)) {
            while (fileScanner.hasNext()) {
                if (fileScanner.hasNextInt()) {
                    numbersList.add(fileScanner.nextInt());
                } else {
                    fileScanner.next(); // skip non-integer
                }
            }
        } catch (FileNotFoundException e) {
            System.out.println("File not found: " + e.getMessage());
            return;
        }

        if (numbersList.isEmpty()) {
            System.out.println("No numbers found in the file.");
            return;
        }

        int[] array = numbersList.stream().mapToInt(i -> i).toArray();

        // Choose sorting algorithm
        System.out.println("Choose sorting algorithm:");
        System.out.println("1. Bubble Sort");
        System.out.println("2. Insertion Sort");
        System.out.println("3. Merge Sort");
        System.out.print("Enter choice (1-3): ");
        int algoChoice = sc.nextInt();

        // Choose sorting order
        System.out.println("Choose sorting order:");
        System.out.println("1. Ascending");
        System.out.println("2. Descending");
        System.out.print("Enter choice (1-2): ");
        int orderChoice = sc.nextInt();
        boolean ascending = orderChoice == 1;

        // Sort and measure time
        long startTime = System.nanoTime();
        switch (algoChoice) {
            case 1 -> bubbleSort(array, ascending);
            case 2 -> insertionSort(array, ascending);
            case 3 -> array = mergeSort(array, ascending);
            default -> {
                System.out.println("Invalid algorithm choice. Exiting...");
                return;
            }
        }
        long endTime = System.nanoTime();
        double timeTaken = (endTime - startTime) / 1_000_000.0;

        // Display results (limit output if large)
        System.out.println("\nSorted Numbers:");
        if (array.length > 100) {
            System.out.println(Arrays.toString(Arrays.copyOfRange(array, 0, 100)) + " ... (truncated, total " + array.length + " numbers)");
        } else {
            for (int num : array) {
                System.out.println(num);
            }
        }
        System.out.printf("\nTime taken: %.3f ms\n", timeTaken);
    }

    // ================= Bubble Sort =================
    private static void bubbleSort(int[] arr, boolean ascending) {
        int n = arr.length;
        boolean swapped;
        for (int i = 0; i < n - 1; i++) {
            swapped = false;
            for (int j = 0; j < n - 1 - i; j++) {
                if (ascending ? arr[j] > arr[j + 1] : arr[j] < arr[j + 1]) {
                    int temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                    swapped = true;
                }
            }
            if (!swapped) break;
        }
    }

    // ================= Insertion Sort =================
    private static void insertionSort(int[] arr, boolean ascending) {
        for (int i = 1; i < arr.length; i++) {
            int key = arr[i];
            int j = i - 1;
            while (j >= 0 && (ascending ? arr[j] > key : arr[j] < key)) {
                arr[j + 1] = arr[j];
                j--;
            }
            arr[j + 1] = key;
        }
    }

    // ================= Merge Sort =================
    private static int[] mergeSort(int[] arr, boolean ascending) {
        if (arr.length <= 1) return arr;

        int mid = arr.length / 2;
        int[] left = Arrays.copyOfRange(arr, 0, mid);
        int[] right = Arrays.copyOfRange(arr, mid, arr.length);

        left = mergeSort(left, ascending);
        right = mergeSort(right, ascending);

        return merge(left, right, ascending);
    }

    private static int[] merge(int[] left, int[] right, boolean ascending) {
        int[] result = new int[left.length + right.length];
        int i = 0, j = 0, k = 0;

        while (i < left.length && j < right.length) {
            if (ascending ? left[i] <= right[j] : left[i] >= right[j]) {
                result[k++] = left[i++];
            } else {
                result[k++] = right[j++];
            }
        }

        while (i < left.length) result[k++] = left[i++];
        while (j < right.length) result[k++] = right[j++];

        return result;
    }
}
