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

    /* ===================== VISUAL STATE ===================== */
    private int i = 0, j = 0;
    private boolean swapped = false;
    private Timer timer;

    /* ===================== TIMING ===================== */
    private double algorithmTimeSeconds;

    /* ===================== UI ===================== */
    private JTextArea outputArea;
    private BarPanel barPanel;
    private JButton loadButton, playButton, stopButton, replayButton, clearButton;
    private JSlider speedSlider;
    private JComboBox<String> algorithmBox;
    private String currentAlgorithm = "Bubble Sort";

    /* ===================== SETTINGS ===================== */
    private static final int MIN_DELAY = 5;
    private static final int MAX_DELAY = 200;
    private static final int MIN_BAR_WIDTH = 4;

    /* ===================== COLORS ===================== */
    private final Color BG = new Color(25, 40, 70);
    private final Color PANEL = new Color(35, 55, 95);
    private final Color TEXT = new Color(220, 220, 220);
    private final Color ACCENT = new Color(100, 160, 220);
    private final Color BAR = new Color(120, 160, 200);
    private final Color COMPARE = new Color(255, 193, 7);
    private final Color SORTED = new Color(60, 180, 100);

    public BubbleSortGUI() {
        setTitle("Sorting Algorithm Visualizer");
        setSize(1200, 650);
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        setLocationRelativeTo(null);
        initUI();
    }

    /* ===================== UI ===================== */
    private void initUI() {
        setLayout(new BorderLayout());
        getContentPane().setBackground(BG);

        JLabel title = new JLabel("Sorting Algorithm Visualizer (Descending)", JLabel.CENTER);
        title.setFont(new Font("Segoe UI", Font.BOLD, 22));
        title.setForeground(ACCENT);
        title.setBorder(new EmptyBorder(10, 10, 10, 10));
        add(title, BorderLayout.NORTH);

        barPanel = new BarPanel();
        outputArea = new JTextArea();
        outputArea.setEditable(false);
        outputArea.setFont(new Font("Consolas", Font.PLAIN, 13));
        outputArea.setBackground(PANEL);
        outputArea.setForeground(TEXT);

        JSplitPane split = new JSplitPane(
                JSplitPane.HORIZONTAL_SPLIT,
                new JScrollPane(barPanel),
                new JScrollPane(outputArea)
        );
        split.setResizeWeight(0.65);
        add(split, BorderLayout.CENTER);

        JPanel controls = new JPanel(new FlowLayout());
        controls.setBackground(BG);

        loadButton = createButton("Load Dataset");
        playButton = createButton("▶ Play");
        stopButton = createButton("⏹ Stop");
        replayButton = createButton("🔄 Replay");
        clearButton = createButton("Clear Output");

        playButton.setEnabled(false);
        stopButton.setEnabled(false);
        replayButton.setEnabled(false);

        speedSlider = new JSlider(MIN_DELAY, MAX_DELAY, 30);
        speedSlider.setPreferredSize(new Dimension(160, 40));
        speedSlider.addChangeListener(e -> {
            if (timer != null) timer.setDelay(getInvertedDelay());
        });

        algorithmBox = new JComboBox<>(new String[]{
                "Bubble Sort", "Selection Sort", "Insertion Sort",
                "Merge Sort", "Quick Sort", "Random Quick Sort"
        });
        algorithmBox.addActionListener(e ->
                currentAlgorithm = (String) algorithmBox.getSelectedItem()
        );

        loadButton.addActionListener(e -> loadDataset());
        playButton.addActionListener(e -> startVisualization());
        stopButton.addActionListener(e -> stopVisualization());
        replayButton.addActionListener(e -> resetVisualization());
        clearButton.addActionListener(e -> outputArea.setText(""));

        controls.add(loadButton);
        controls.add(playButton);
        controls.add(stopButton);
        controls.add(replayButton);
        controls.add(algorithmBox);
        controls.add(speedSlider);
        controls.add(clearButton);

        add(controls, BorderLayout.SOUTH);
    }

    /* ===================== DATA LOADING & DISPLAY ===================== */
    private void loadDataset() {
        File file = chooseFile();
        if (file == null) return;

        try (BufferedReader br = new BufferedReader(new FileReader(file))) {
            ArrayList<Integer> list = new ArrayList<>();
            String line;
            while ((line = br.readLine()) != null)
                list.add(Integer.parseInt(line.trim()));

            originalArray = list.stream().mapToInt(Integer::intValue).toArray();
            maxValue = findMax(originalArray);

            visualArray = originalArray.clone();

            algorithmTimeSeconds = measureAlgorithmTime();

            int[] sortedArray = originalArray.clone();
            sortArray(sortedArray);

            outputArea.setText(
                    "📁 Dataset: " + file.getName() + "\n" +
                    "Array Size: " + originalArray.length + "\n" +
                    "Algorithm: " + currentAlgorithm + "\n" +
                    String.format("⏱ Algorithm Time: %.6f seconds\n", algorithmTimeSeconds) +
                    "\nOriginal Array:\n" + arrayToString(originalArray) +
                    "\n\nSorted Array (Descending):\n" + arrayToString(sortedArray) +
                    "\n\n▶ Press Play to visualize"
            );

            resetVisualization();
            playButton.setEnabled(true);
            replayButton.setEnabled(true);

        } catch (Exception e) {
            outputArea.setText("❌ Error loading dataset\n" + e.getMessage());
        }
    }

    /* ===================== ARRAY HELPERS ===================== */
    private String arrayToString(int[] arr) {
        StringBuilder sb = new StringBuilder();
        for (int k = 0; k < arr.length; k++) {
            sb.append(arr[k]);
            if (k < arr.length - 1) sb.append(", ");
            if ((k + 1) % 20 == 0) sb.append("\n");
        }
        return sb.toString();
    }

    private void sortArray(int[] arr) {
        switch (currentAlgorithm) {
            case "Bubble Sort": bubbleSortPure(arr); break;
            case "Selection Sort": selectionSortPure(arr); break;
            case "Insertion Sort": insertionSortPure(arr); break;
            case "Merge Sort": mergeSortPure(arr, 0, arr.length - 1); break;
            case "Quick Sort": quickSortPure(arr, 0, arr.length - 1, false); break;
            case "Random Quick Sort": quickSortPure(arr, 0, arr.length - 1, true); break;
        }
    }

    private double measureAlgorithmTime() {
        int[] arr = originalArray.clone();
        long start = System.nanoTime();
        sortArray(arr);
        return (System.nanoTime() - start) / 1_000_000_000.0;
    }

    /* ===================== PURE SORTS ===================== */
    private void bubbleSortPure(int[] a) { 
        for (int i = 0; i < a.length - 1; i++) { 
            boolean swapped=false; 
            for (int j=0;j<a.length-i-1;j++){
                if(a[j]<a[j+1]){swap(a,j,j+1);swapped=true;}
            } 
            if(!swapped) break;
        }
    }
    private void selectionSortPure(int[] a){
        for(int i=0;i<a.length-1;i++){
            int max=i;
            for(int j=i+1;j<a.length;j++) if(a[j]>a[max]) max=j;
            swap(a,i,max);
        }
    }
    private void insertionSortPure(int[] a){
        for(int i=1;i<a.length;i++){
            int key=a[i], j=i-1;
            while(j>=0 && a[j]<key){a[j+1]=a[j]; j--;}
            a[j+1]=key;
        }
    }
    private void mergeSortPure(int[] a,int l,int r){
        if(l>=r) return;
        int m=(l+r)/2;
        mergeSortPure(a,l,m);
        mergeSortPure(a,m+1,r);
        mergePure(a,l,m,r);
    }
    private void mergePure(int[] a,int l,int m,int r){
        int[] t=new int[r-l+1];
        int i=l,j=m+1,k=0;
        while(i<=m && j<=r) t[k++]=a[i]>a[j]?a[i++]:a[j++];
        while(i<=m) t[k++]=a[i++];
        while(j<=r) t[k++]=a[j++];
        System.arraycopy(t,0,a,l,t.length);
    }
    private void quickSortPure(int[] a,int l,int h,boolean random){
        if(l<h){
            int p=partitionPure(a,l,h,random);
            quickSortPure(a,l,p-1,random);
            quickSortPure(a,p+1,h,random);
        }
    }
    private int partitionPure(int[] a,int l,int h,boolean random){
        if(random) swap(a,l+(int)(Math.random()*(h-l+1)),h);
        int pivot=a[h],i=l-1;
        for(int j=l;j<h;j++) if(a[j]>pivot) swap(a,++i,j);
        swap(a,i+1,h);
        return i+1;
    }
    private void swap(int[] a,int x,int y){int t=a[x];a[x]=a[y];a[y]=t;}

    /* ===================== VISUAL SORT ===================== */
    private void startVisualization() {
        stopVisualization();
        playButton.setEnabled(false);
        stopButton.setEnabled(true);
        i = j = 0;
        swapped = false;

        timer = new Timer(getInvertedDelay(), e -> {
            if (i < visualArray.length - 1) {
                if (j < visualArray.length - i - 1) {
                    if (visualArray[j] < visualArray[j + 1]) { swap(visualArray,j,j+1); swapped=true;}
                    j++;
                } else {
                    if(!swapped) i=visualArray.length;
                    swapped=false;
                    j=0;
                    i++;
                }
                barPanel.repaint();
            } else stopVisualization();
        });
        timer.start();
    }

    private void stopVisualization() { 
        if(timer!=null) timer.stop(); 
        playButton.setEnabled(true); 
        stopButton.setEnabled(false);
    }
    private void resetVisualization() { 
        if(originalArray!=null){visualArray=originalArray.clone(); i=j=0; barPanel.repaint();}
    }

    /* ===================== HELPERS ===================== */
    private int getInvertedDelay(){return MAX_DELAY-speedSlider.getValue()+MIN_DELAY;}
    private int findMax(int[] a){int m=a[0]; for(int v:a)m=Math.max(m,v); return m;}
    private JButton createButton(String t){
        JButton b=new JButton(t); 
        b.setBackground(new Color(50,80,130)); 
        b.setForeground(TEXT); 
        b.setFocusPainted(false); 
        b.setPreferredSize(new Dimension(150,38)); 
        return b;
    }
    private File chooseFile(){JFileChooser fc=new JFileChooser(); return fc.showOpenDialog(this)==JFileChooser.APPROVE_OPTION?fc.getSelectedFile():null;}

    /* ===================== BAR PANEL ===================== */
    private class BarPanel extends JPanel {
        public BarPanel(){setBackground(PANEL);}
        protected void paintComponent(Graphics g) {
            super.paintComponent(g);
            if (visualArray==null) return;
            int width = getWidth();
            int height = getHeight() - 20;
            int barWidth = Math.max(width / visualArray.length, MIN_BAR_WIDTH);
            for(int k=0;k<visualArray.length;k++){
                Color barColor = (k >= visualArray.length - i)?SORTED:(k==j||k==j+1)?COMPARE:BAR;
                g.setColor(barColor);
                int bh = (int)((double)visualArray[k]/maxValue * height);
                g.fillRect(k*barWidth, height-bh, barWidth-1, bh);
            }
        }
        public Dimension getPreferredSize(){ 
            return visualArray==null?super.getPreferredSize(): new Dimension(Math.max(visualArray.length*MIN_BAR_WIDTH, getWidth()), 500);
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new BubbleSortGUI().setVisible(true));
    }
}
