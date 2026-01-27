import java.awt.*;
import java.awt.event.ActionEvent;
import java.io.*;
import java.util.ArrayList;
import javax.swing.*;
import javax.swing.border.TitledBorder;

public class BubbleSortGUI extends JFrame {

    private JTextArea originalArea;
    private JTextArea sortedArea;
    private JTextArea timeArea;

    private JComboBox<String> algorithmBox;
    private JRadioButton ascButton;
    private JRadioButton descButton;

    private ArrayList<String> data = new ArrayList<>();

    public BubbleSortGUI() {
        setTitle("Sorting Algorithm");
        setSize(1100, 500);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);

        Color purple = new Color(128, 0, 128);
        Color lightPurple = new Color(230, 200, 255);

        // Main panel
        JPanel mainPanel = new JPanel(new BorderLayout());
        mainPanel.setBackground(lightPurple);

        // Top controls
        JPanel controlPanel = new JPanel();
        controlPanel.setBackground(lightPurple);

        JButton loadButton = new JButton("Load File");
        JButton sortButton = new JButton("Sort");

        String[] algorithms = {
                "Bubble Sort",
                "Insertion Sort",
                "Quick Sort",
                "Merge Sort"
        };
        algorithmBox = new JComboBox<>(algorithms);

        ascButton = new JRadioButton("Ascending", true);
        descButton = new JRadioButton("Descending");

        ButtonGroup orderGroup = new ButtonGroup();
        orderGroup.add(ascButton);
        orderGroup.add(descButton);

        controlPanel.add(loadButton);
        controlPanel.add(new JLabel("Algorithm:"));
        controlPanel.add(algorithmBox);
        controlPanel.add(ascButton);
        controlPanel.add(descButton);
        controlPanel.add(sortButton);

        // Text areas
        originalArea = createTextArea("Original Data", purple);
        sortedArea = createTextArea("Sorted Data", purple);
        timeArea = createTextArea("Time Taken", purple);
        timeArea.setEditable(false);

        JPanel textPanel = new JPanel(new GridLayout(1, 3, 10, 10));
        textPanel.setBackground(lightPurple);
        textPanel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));

        textPanel.add(new JScrollPane(originalArea));
        textPanel.add(new JScrollPane(sortedArea));
        textPanel.add(new JScrollPane(timeArea));

        mainPanel.add(controlPanel, BorderLayout.NORTH);
        mainPanel.add(textPanel, BorderLayout.CENTER);

        add(mainPanel);

        // Button actions
        loadButton.addActionListener(this::loadFile);
        sortButton.addActionListener(this::sortData);
    }

    private JTextArea createTextArea(String title, Color borderColor) {
        JTextArea area = new JTextArea();
        area.setBorder(BorderFactory.createTitledBorder(
                BorderFactory.createLineBorder(borderColor, 2),
                title,
                TitledBorder.CENTER,
                TitledBorder.TOP
        ));
        area.setFont(new Font("Monospaced", Font.PLAIN, 14));
        return area;
    }

    private void loadFile(ActionEvent e) {
        JFileChooser chooser = new JFileChooser();
        int result = chooser.showOpenDialog(this);

        if (result == JFileChooser.APPROVE_OPTION) {
            File file = chooser.getSelectedFile();
            data.clear();
            originalArea.setText("");
            sortedArea.setText("");
            timeArea.setText("");

            try (BufferedReader br = new BufferedReader(new FileReader(file))) {
                String line;
                while ((line = br.readLine()) != null) {
                    data.add(line);
                    originalArea.append(line + "\n");
                }
            } catch (IOException ex) {
                JOptionPane.showMessageDialog(this, "Error reading file.");
            }
        }
    }

    private void sortData(ActionEvent e) {
        if (data.isEmpty()) {
            JOptionPane.showMessageDialog(this, "Load a file first!");
            return;
        }

        String[] array = data.toArray(new String[0]);
        boolean ascending = ascButton.isSelected();
        String algorithm = (String) algorithmBox.getSelectedItem();

        long startTime = System.nanoTime();

        switch (algorithm) {
            case "Bubble Sort":
                bubbleSort(array, ascending);
                break;
            case "Insertion Sort":
                insertionSort(array, ascending);
                break;
            case "Quick Sort":
                quickSort(array, 0, array.length - 1, ascending);
                break;
            case "Merge Sort":
                mergeSort(array, 0, array.length - 1, ascending);
                break;
        }

        long endTime = System.nanoTime();

        sortedArea.setText("");
        for (String s : array) {
            sortedArea.append(s + "\n");
        }

        long duration = endTime - startTime;
        timeArea.setText(
                "Algorithm: " + algorithm + "\n" +
                "Order: " + (ascending ? "Ascending" : "Descending") + "\n\n" +
                "Time (ns): " + duration + "\n" +
                "Time (ms): " + (duration / 1_000_000.0)
        );
    }

    // ================= SORTING ALGORITHMS =================

    private void bubbleSort(String[] arr, boolean asc) {
        for (int i = 0; i < arr.length - 1; i++) {
            for (int j = 0; j < arr.length - i - 1; j++) {
                if (compare(arr[j], arr[j + 1], asc)) {
                    swap(arr, j, j + 1);
                }
            }
        }
    }

    private void insertionSort(String[] arr, boolean asc) {
        for (int i = 1; i < arr.length; i++) {
            String key = arr[i];
            int j = i - 1;
            while (j >= 0 && compare(arr[j], key, asc)) {
                arr[j + 1] = arr[j];
                j--;
            }
            arr[j + 1] = key;
        }
    }

    private void quickSort(String[] arr, int low, int high, boolean asc) {
        if (low < high) {
            int pi = partition(arr, low, high, asc);
            quickSort(arr, low, pi - 1, asc);
            quickSort(arr, pi + 1, high, asc);
        }
    }

    private int partition(String[] arr, int low, int high, boolean asc) {
        String pivot = arr[high];
        int i = low - 1;
        for (int j = low; j < high; j++) {
            if (!compare(arr[j], pivot, asc)) {
                i++;
                swap(arr, i, j);
            }
        }
        swap(arr, i + 1, high);
        return i + 1;
    }

    private void mergeSort(String[] arr, int left, int right, boolean asc) {
        if (left < right) {
            int mid = (left + right) / 2;
            mergeSort(arr, left, mid, asc);
            mergeSort(arr, mid + 1, right, asc);
            merge(arr, left, mid, right, asc);
        }
    }

    private void merge(String[] arr, int left, int mid, int right, boolean asc) {
        int n1 = mid - left + 1;
        int n2 = right - mid;

        String[] L = new String[n1];
        String[] R = new String[n2];

        System.arraycopy(arr, left, L, 0, n1);
        System.arraycopy(arr, mid + 1, R, 0, n2);

        int i = 0, j = 0, k = left;

        while (i < n1 && j < n2) {
            if (!compare(L[i], R[j], asc)) {
                arr[k++] = L[i++];
            } else {
                arr[k++] = R[j++];
            }
        }

        while (i < n1) arr[k++] = L[i++];
        while (j < n2) arr[k++] = R[j++];
    }

    private boolean compare(String a, String b, boolean asc) {
        return asc ? a.compareTo(b) > 0 : a.compareTo(b) < 0;
    }

    private void swap(String[] arr, int i, int j) {
        String temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
    }

    // ================= MAIN =================

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new BubbleSortGUI().setVisible(true));
    }
}