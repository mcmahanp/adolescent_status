library(lme4)
library(lmerTest)

library(xtable)


dta <- read.csv("") # /path/to/merged.csv
outputDir <- "output/regressions/"


## useful functions:
groupMeanCenter <- function(x,groups){
    means <- aggregate(x,by=list(groups),FUN = mean, na.rm=TRUE)
    groupMeans <- means[[2]][match(groups,means[[1]])]
    return(x-groupMeans)
}
standardize <- function(x){
    if(length(unique(x))>3){
        return((x-mean(x,na.rm=TRUE))/sd(x,na.rm=TRUE))
    }else{
        return(x)
    }
}
significant_coefs <- function(ci){
    sc <- (ci[,2]+ci[,1])/2
    sc[sign(ci[,1])*sign(ci[,2])<0] <- NA 
    return(sc)
}

mdTable.merMod <- function(l,file){
     pp <- capture.output(print(summary(l)))
     reRow <- which(pp=='Random effects:')
     feRow <- which(pp=='Fixed effects:')
     nRows <- which(substr(pp,1,13)=='Signif. codes')
     if(length(nRows)==0){nRows <- length(pp)}

     # fixed effects
     feHeader <- pp[feRow+1]
     substr(feHeader,2,18) <- "**Fixed Effects**"
     startPos <- sapply(c('Estimate','Std. Error', 'z value' ,'Pr(>|z|)'),regexpr,text=feHeader,fixed=TRUE)
     feSep <- paste(rep('-',nchar(feHeader)),collapse='')
     startPos['Estimate'] <- startPos['Estimate'] -2
     for(p in startPos){
        substr(feSep,p-1,p) <- ' '
     }
     feData <- pp[(feRow+2):(nRows-2)]
     feData <- gsub('*','',feData,fixed=TRUE)
     feTable <- paste(c(feHeader,feSep,feData),collapse='\n')

     # random effects
     reHeader <- pp[reRow+1]
     startPos <- sapply(c('Name','Variance','Std.Dev.'),regexpr,text=reHeader,fixed=TRUE)
     reSep <- paste(rep('-',nchar(reHeader)),collapse='')
     for(p in startPos){
        substr(reSep,p-1,p) <- ' '
     }
     reData <- pp[(reRow+2):(feRow-3)]
     reTable <- paste(c(reHeader,reSep,reData),collapse='\n')

     writeLines(c(feTable,'\n',reTable),file)
}
saveRegr.merMod <- function(l,file,method='Wald'){
    cfs <- coef(l)
    cfs_mean <- sapply(cfs[[1]],mean)
    cfnt <- confint(l,method=method)
    n <- length(resid(l))
    estimates <- cfs_mean[match(names(cfs_mean),rownames(cfnt))]
    cNames <- intersect(rownames(cfnt),names(estimates))
    est <- data.frame(
        estimate=cfs_mean[match(names(cfs_mean),rownames(cfnt))][cNames],
        cfnt[cNames,],
        n=n
    )
    est <- rbind(est,theta=c(l@theta,NA,NA,NA))
    est <- rbind(est,numGroups=c(l@Gp[2],NA,NA,NA))
    write.csv(est,file=sprintf('%s.csv',file))
    mdTable.merMod(l,sprintf('%s.md',file))
}



#############
# These are the two regressions to make sense
# of embeddedness vs rank.
# Embeddedness is the proporion of your school that
# you are in direct hierarcy with.
# Rank is the proportion of your school that you are
# higher status than.
#############


f_inschool_embeddedness <-hSizeProp_95_l_std ~ 
                                      # sociometric
                                      friend_indegree+#friend_outdegree+
                                      # demographics
                                      female + gradeCenteredAge +
                                      hispanic.x*gradePropHispanic+
                                      black.x*gradePropBlack+
                                      asian.x*gradePropAsian+
                                      amind*gradePropAmind+
                                      other+ bornInUS +
                                      # health and behavior
                                      memb_langClub+memb_compClub+memb_debateClub+memb_dramaClub+memb_mathClub+memb_scienceClub+memb_bandClub+memb_cheerClub+memb_choirClub+memb_newspaperClub+memb_honorClub+memb_stCouncilClub+memb_yearbookClub+
                                      memb_baseballTeam+memb_basketballTeam+memb_fHockeyTeam+memb_footballTeam+memb_iHockeyTeam+memb_soccerTeam+memb_swimTeam+memb_tennisTeam+memb_trackTeam+memb_volleyballTeam+memb_wrestlingTeam+memb_otherTeam+
                                      #intercept
                                      standardize(gradeSize) +
                                      # random effects
                                      (1 | schoolGrade)
summary(l_inschool_embeddedness <- lmer(f_inschool_embeddedness,data=dta))
saveRegr.merMod(l_inschool_embeddedness,paste(outputDir,'l_inschool_embeddedness',collapse=''))

f_inschool_rank <-hPropBelow_95_l_std ~ 
                                      # sociometric
                                      friend_indegree+#friend_outdegree+
                                      # demographics
                                      female + gradeCenteredAge +
                                      hispanic.x*gradePropHispanic+
                                      black.x*gradePropBlack+
                                      asian.x*gradePropAsian+
                                      amind*gradePropAmind+
                                      other+ bornInUS +
                                      # health and behavior
                                      memb_langClub+memb_compClub+memb_debateClub+memb_dramaClub+memb_mathClub+memb_scienceClub+memb_bandClub+memb_cheerClub+memb_choirClub+memb_newspaperClub+memb_honorClub+memb_stCouncilClub+memb_yearbookClub+
                                      memb_baseballTeam+memb_basketballTeam+memb_fHockeyTeam+memb_footballTeam+memb_iHockeyTeam+memb_soccerTeam+memb_swimTeam+memb_tennisTeam+memb_trackTeam+memb_volleyballTeam+memb_wrestlingTeam+memb_otherTeam+
                                      #intercept
                                      standardize(gradeSize) +
                                      # random effects
                                      (1 | schoolGrade)
summary(l_inschool_rank <- lmer(f_inschool_rank,data=dta))
saveRegr.merMod(l_inschool_rank,paste(outputDir,'l_inschool_rank',collapse=''))


