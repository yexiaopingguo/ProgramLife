import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.InputStreamReader;


/**
 * 图灵Mark老师
 */
public class JavaFFMpeg extends Thread{
    private String ffmpegCmd = "";
    public String getTheFmpgCmdLine () {
        return ffmpegCmd;
    }
    public void setTheFmpgCmdLine (String theFmpgCmdLine) {
        this.ffmpegCmd = theFmpgCmdLine;
    }

    public void run(){
            openFFmpegExe();
            System.out.println("执行完成，准备退出");
    }
    private void openFFmpegExe () {
        if (ffmpegCmd == null || ffmpegCmd.equals("")) {
            return;
        }
        //开启一个进程
        Runtime rn = Runtime.getRuntime();
        Process p = null;
        try {
            //传递ffmpeg推流命令行
            p = rn.exec(ffmpegCmd);
            //ffmpeg输出的都是"错误流": stdin,stdout,stderm,
            BufferedInputStream in = new BufferedInputStream(p.getErrorStream());
            BufferedReader inBr = new BufferedReader(new InputStreamReader(in));
            String lineStr;
            System.out.println("开始...");
            while ((lineStr = inBr.readLine()) != null) {
                //获得命令执行后在控制台的输出信息
                System.out.println(lineStr);//打印输出信息
            }
            inBr.close();
            in.close();
        } catch (Exception e) {
            System.out.println("异常: " + e.getMessage());
        }
    }

    public static void main(String[] args) throws Exception {
        System.out.println ( " ---开始推流---") ;
        JavaFFMpeg javaFFMpeg = new JavaFFMpeg();
        String ffmpegCmd = "D:\\TuLing\\VIPL\\Live\\src\\ffmpeg\\bin\\ffmpeg -re -i D:\\Temp\\03.mp4 -c copy -f flv rtmp://124.221.103.27:1935/hls1/test" ;
        javaFFMpeg.setTheFmpgCmdLine (ffmpegCmd);
        javaFFMpeg.start ();
        javaFFMpeg.join() ;
        System .out.println ( "---结束推流---" );
    }
}
