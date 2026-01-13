import java.awt.*;
import java.io.*;
import java.util.ArrayList;
import javax.swing.*;
import javax.swing.border.EmptyBorder;

public class BubbleSortGUI extends JFrame {

    /* ===================== DATA ===================== */
    private int[] originalArray;
    private int[] visualArray;
    private int maxValue;

    /* ===================== SORT STATE ===================== */
    private int i = 0, j = 0;
    private boolean swapped = false;
    private Timer timer;

    /* ===================== UI COMPONENTS ===================== */
    private JTextArea outputArea;
    private BarPanel barPanel;

    private JButton loadButton;
    private JButton playButton;
    private JButton stopButton;
    private JButton replayButton;
    private JButton clearButton;

    private JSlider speedSlider;

    /* ===================== COLORS ===================== */
    private final Color BG = new Color(30, 30, 30);
    private final Color PANEL = new Color(40, 40, 40);
    private final Color TEXT = new Color(220, 220, 220);
    private final Color ACCENT = new Color(70, 130, 180);
    private final Color BAR = new Color(120, 120, 120);
    private final Color COMPARE = new Color(255, 193, 7);
    private final Color SORTED = new Color(40, 167, 69);

    public BubbleSortGUI() {
        setTitle("Bubble Sort (Descending) – Visualizer");
        setSize(1200, 650);
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        setLocationRelativeTo(null);
        initUI();
    }

    /* ===================== UI SETUP ===================== */
    private void initUI() {
        getContentPane().setBackground(BG);
        setLayout(new BorderLayout(10, 10));

        JLabel title = new JLabel("Bubble Sort (Descending Order)", JLabel.CENTER);
        title.setFont(new Font("Segoe UI", Font.BOLD, 22));
        title.setForeground(ACCENT);
        title.setBorder(new EmptyBorder(10, 10, 10, 10));
        add(title, BorderLayout.NORTH);

        JSplitPane splitPane = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT);
        splitPane.setResizeWeight(0.6);
        splitPane.setBorder(null);

        barPanel = new BarPanel();
        splitPane.setLeftComponent(barPanel);

        outputArea = new JTextArea();
        outputArea.setEditable(false);
        outputArea.setFont(new Font("Consolas", Font.PLAIN, 13));
        outputArea.setBackground(PANEL);
        outputArea.setForeground(TEXT);
        outputArea.setBorder(new EmptyBorder(10, 10, 10, 10));

        splitPane.setRightComponent(new JScrollPane(outputArea));
        add(splitPane, BorderLayout.CENTER);

        JPanel controls = new JPanel(new FlowLayout(FlowLayout.CENTER, 10, 10));
        controls.setBackground(BG);

        loadButton = createButton("Load Dataset");
        playButton = createButton("▶ Play");
        stopButton = createButton("⏹ Stop");
        replayButton = createButton("🔄 Replay");
        clearButton = createButton("Clear Output");

        playButton.setEnabled(false);
        stopButton.setEnabled(false);
        replayButton.setEnabled(false);

        speedSlider = new JSlider(5, 200, 30);
        speedSlider.setPreferredSize(new Dimension(160, 40));
        speedSlider.setBackground(BG);
        speedSlider.setForeground(TEXT);
        speedSlider.setToolTipText("Animation Speed");

        speedSlider.addChangeListener(e -> {
            if (timer != null) {
                timer.setDelay(speedSlider.getValue());
            }
        });

        loadButton.addActionListener(e -> loadDataset());
        playButton.addActionListener(e -> startVisualization());
        stopButton.addActionListener(e -> stopVisualization());
        replayButton.addActionListener(e -> replayVisualization());
        clearButton.addActionListener(e -> outputArea.setText(""));

        controls.add(loadButton);
        controls.add(playButton);
        controls.add(stopButton);
        controls.add(replayButton);
        controls.add(new JLabel("Speed"));
        controls.add(speedSlider);
        controls.add(clearButton);

        add(controls, BorderLayout.SOUTH);
    }

    /* ===================== DATA LOADING ===================== */
    private void loadDataset() {
        File file = chooseFile();
        if (file == null) return;

        try {
            ArrayList<Integer> list = new ArrayList<>();
            BufferedReader br = new BufferedReader(new FileReader(file));
            String line;
            while ((line = br.readLine()) != null) {
                list.add(Integer.parseInt(line.trim()));
            }
            br.close();

            originalArray = list.stream().mapToInt(i -> i).toArray();
            visualArray = originalArray.clone();
            maxValue = findMax(originalArray);

            outputArea.setText(
                "📁 Dataset File: " + file.getName() + "\n\n" +
                "Original Array:\n" + arrayToString(originalArray) + "\n\n" +
                "Array Size: " + originalArray.length + "\n" +
                "Algorithm: Bubble Sort (Descending)"
            );

            i = j = 0;
            swapped = false;
            playButton.setEnabled(true);
            replayButton.setEnabled(true);
            barPanel.repaint();

        } catch (Exception e) {
            outputArea.setText("❌ Error reading dataset\n" + e.getMessage());
        }
    }

    /* ===================== VISUAL SORT ===================== */
    private void startVisualization() {
        playButton.setEnabled(false);
        stopButton.setEnabled(true);

        timer = new Timer(speedSlider.getValue(), e -> {
            if (i < visualArray.length) {
                if (j < visualArray.length - i - 1) {
                    if (visualArray[j] < visualArray[j + 1]) {
                        swap(visualArray, j, j + 1);
                        swapped = true;
                    }
                    j++;
                } else {
                    if (!swapped) i = visualArray.length;
                    swapped = false;
                    j = 0;
                    i++;
                }
                barPanel.repaint();
            } else {
                stopVisualization();
            }
        });

        timer.start();
    }

    private void stopVisualization() {
        if (timer != null) timer.stop();
        playButton.setEnabled(true);
        stopButton.setEnabled(false);
    }

    private void replayVisualization() {
        stopVisualization();
        visualArray = originalArray.clone();
        i = j = 0;
        swapped = false;
        barPanel.repaint();
    }

    /* ===================== HELPERS ===================== */
    private int findMax(int[] arr) {
        int max = arr[0];
        for (int v : arr) max = Math.max(max, v);
        return max;
    }

    private void swap(int[] arr, int a, int b) {
        int t = arr[a];
        arr[a] = arr[b];
        arr[b] = t;
    }

    private String arrayToString(int[] arr) {
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < arr.length; i++) {
            sb.append(arr[i]);
            if (i < arr.length - 1) sb.append(", ");
        }
        return sb.append("]").toString();
    }

    private File chooseFile() {
        JFileChooser chooser = new JFileChooser();
        chooser.setDialogTitle("Select Dataset File");
        return chooser.showOpenDialog(this) == JFileChooser.APPROVE_OPTION
                ? chooser.getSelectedFile() : null;
    }

    private JButton createButton(String text) {
        JButton b = new JButton(text);
        b.setFont(new Font("Segoe UI", Font.BOLD, 13));
        b.setBackground(new Color(60, 60, 60));
        b.setForeground(TEXT);
        b.setFocusPainted(false);
        b.setBorder(BorderFactory.createLineBorder(ACCENT));
        b.setPreferredSize(new Dimension(150, 38));
        return b;
    }

    /* ===================== BAR VISUALIZER ===================== */
    private class BarPanel extends JPanel {

        BarPanel() {
            setBackground(PANEL);
            setDoubleBuffered(true);
        }

        @Override
        protected void paintComponent(Graphics g) {
            super.paintComponent(g);
            if (visualArray == null) return;

            Graphics2D g2 = (Graphics2D) g;
            g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING,
                                RenderingHints.VALUE_ANTIALIAS_ON);

            int width = getWidth();
            int height = getHeight();
            int usableHeight = height - 40;

            int barWidth = Math.max(2, width / visualArray.length);

            for (int k = 0; k < visualArray.length; k++) {

                if (k >= visualArray.length - i)
                    g2.setColor(SORTED);
                else if (k == j || k == j + 1)
                    g2.setColor(COMPARE);
                else
                    g2.setColor(BAR);

                double ratio = visualArray[k] / (double) maxValue;
                int barHeight = (int) (ratio * usableHeight);

                int x = k * barWidth;
                int y = height - barHeight - 10;

                g2.fillRoundRect(
                    x,
                    y,
                    barWidth - 1,
                    barHeight,
                    4,
                    4
                );
            }
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new BubbleSortGUI().setVisible(true));
    }
}
