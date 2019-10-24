[num,txt,raw] = xlsread('C:\Users\Lisa\Desktop\20180117_node1.xlsx')

stepfcn = zeros(1,1440)
k=size(num)
a=k(1,1)

for i = 1:a
    a=txt{i+1,1}
    b=txt{i+1,2}
    split1 =  strsplit(a,' ')
    k=split1{2}
    split2 = strsplit(k,'_')
    split3 =  strsplit(b,' ')
    k=split3{2}
    split4 = strsplit(k,'_')
    h1=split2{1}
    m1=split2{2}
    h2=split4{1}
    m2=split4{2}
    startpoint = str2num(h1)*60+str2num(m1)
    endpoint = str2num(h2)*60+str2num(m2)
    for j =startpoint:endpoint
        stepfcn(1,j)=1
    end
end
startDate = datenum('01-17-2018');
endDate = datenum('01-18-2018');
xData = linspace(startDate,endDate,1440);
figure
stairs(xData,stepfcn)
datetick('x','HH','keepticks')
ylim([-1 2])
title('node2')

