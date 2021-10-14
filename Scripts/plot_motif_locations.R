library(dplyr)
library(tidyr)
library(ggplot2)
library(formattable)
library(patchwork)


#generate initial bin data in workable format
work_bins <- read.csv("zm_random_norm_bins.csv", header = TRUE)
work_bins

colnames(work_bins)[colnames(work_bins) == "X"] <- "Motif"
colnames(work_bins) <- gsub("X","",colnames(work_bins))
colnames(work_bins) <- gsub("S","",colnames(work_bins))
colnames(work_bins) <- gsub("C","",colnames(work_bins))

work_bins <- work_bins %>% pivot_longer(-Motif, names_to="Bins", values_to="Count") #%>% subset(Motif != "AAAAAAA")

work_bins$Bins <- factor(work_bins$Bins, levels = unique(work_bins$Bins))
work_bins
#graph of raw count if you want....
p1 <- ggplot(work_bins, aes(x=Bins, y=Count, group=Motif))+
  geom_line(aes(linetype=Motif))+
  geom_point()
p1

#wrangle data to be percentage based + mean line
g <- work_bins %>%
  group_by(Motif, Bins) %>% 
  summarise(cnt = Count) %>% 
  mutate(freq = formattable::percent((cnt/sum(cnt))*100))
g
#mean line
tt <- work_bins %>%
  subset(select = -Motif) %>% 
  group_by(Bins) %>% 
  summarise(Count=sum(Count)) %>% 
  mutate(freq = formattable::percent((Count/sum(Count))*100))
tt

#set factor to be the unique values of Bins eg. U1 N1 D1
g$Bins <- factor(g$Bins, levels = unique(g$Bins))

colors <- c("Mean Motif Position" = "deepskyblue4", "Individual Motifs" = "azure3")

p2 <- ggplot(g, aes(x=Bins, y=freq))+
  geom_line(aes(group=Motif, color = "Individual Motifs"), alpha=0.4)+
  geom_point(size=0.5, alpha = 0.2) + 
  geom_line(data=tt, aes(x=Bins, y=freq, group=1, color = "Mean Motif Position"),
            size = 2.0)+
  labs(x="5% intervals of Sequence (Eg. 1=0-5%, 2=5-10% ... 20=95-100%)
       U=upstream flank    N=lncrna    D=downstream flank", y="frequency %", color = "Legend")+
  scale_color_manual(values = colors) +
  ggtitle("Significant Motifs for random Seq Position Frequency Within Sequence for Zea mays")+
  theme_bw()+
  theme(plot.title = element_text(hjust=0.5))
p2


# make random graph (needs to be generated values in python first)
