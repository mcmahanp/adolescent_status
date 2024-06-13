groupMeanCenter <- function(x,groups){
    means <- aggregate(x,by=list(groups),FUN = mean, na.rm=TRUE)
    groupMeans <- means[[2]][match(groups,means[[1]])]
    return(x-groupMeans)
}
standardize <- function(x){
    return((x-mean(x,na.rm=TRUE))/sd(x,na.rm=TRUE))
}
logit <- function(p){return(log(p/(1-p)))}


# read the data
studentData <- read.csv("") # /path/to/students_inschool.csv
keyData <- read.csv("") # /path/to/key.csv
statusData <- read.csv("output/nodeData.csv")
gradeData <- read.csv("output/gradeData.csv")


# merge
dta <- merge(keyData,statusData,by="fakeId")
dta <- merge(studentData,dta,by.x='aid',by.y='realId')

dta <- dta[!is.na(dta$schoolCode) & !is.na(dta$grade.x),]
dta$commId <- dta$schoolCode
dta$commId[dta$commId>99] <- dta$commId[dta$commId>99]-100
dta <- merge(dta,gradeData[gradeData$cutoff==.9,],by.x=c('commId','grade.x'),by.y=c('schoolNum','gradeNum'),all=TRUE)


# calculate variables
# school/grade Size
dta$schoolGrade <- paste(dta$commId,dta$grade.x)
# grade size
gradeSize <- aggregate(dta$schoolGrade,by=dta['schoolGrade'],FUN=length)
names(gradeSize) <- c('schoolGrade','gradeSize')
dta <- merge(dta,gradeSize,all=TRUE)# grade size
#grade mean age and mean-centered age
gradeMeanAge <- aggregate(dta$age,by=dta['schoolGrade'],FUN=mean,na.rm=TRUE)
names(gradeMeanAge) <- c('schoolGrade','gradeMeanAge')
dta <- merge(dta,gradeMeanAge,all=TRUE)
dta$gradeCenteredAge <- dta$age-dta$gradeMeanAge
# comm size
commSize <- aggregate(dta$commId,by=dta['commId'],FUN=length)
names(commSize) <- c('commId','commSize')
dta <- merge(dta,commSize,all=TRUE)
# comm proportion white
commPropWhite <- aggregate(dta$white.x,by=dta['commId'],FUN=mean,na.rm=TRUE)
names(commPropWhite) <- c('commId','commPropWhite')
dta <- merge(dta,commPropWhite,all=TRUE)
# comm proportion black
commPropBlack <- aggregate(dta$black.x,by=dta['commId'],FUN=mean,na.rm=TRUE)
names(commPropBlack) <- c('commId','commPropBlack')
dta <- merge(dta,commPropBlack,all=TRUE)
# grade proportion white
gradePropWhite <- aggregate(dta$white.x,by=dta['schoolGrade'],FUN=mean,na.rm=TRUE)
names(gradePropWhite) <- c('schoolGrade','gradePropWhite')
dta <- merge(dta,gradePropWhite,all=TRUE)
# grade proportion black
gradePropBlack <- aggregate(dta$black.x,by=dta['schoolGrade'],FUN=mean,na.rm=TRUE)
names(gradePropBlack) <- c('schoolGrade','gradePropBlack')
dta <- merge(dta,gradePropBlack,all=TRUE)
# grade proportion hispanic
gradePropHispanic <- aggregate(dta$hispanic.x,by=dta['schoolGrade'],FUN=mean,na.rm=TRUE)
names(gradePropHispanic) <- c('schoolGrade','gradePropHispanic')
dta <- merge(dta,gradePropHispanic,all=TRUE)
# grade proportion asian
gradePropAsian <- aggregate(dta$asian.x,by=dta['schoolGrade'],FUN=mean,na.rm=TRUE)
names(gradePropAsian) <- c('schoolGrade','gradePropAsian')
dta <- merge(dta,gradePropAsian,all=TRUE)
# grade proportion american indian
gradePropAmind <- aggregate(dta$amind,by=dta['schoolGrade'],FUN=mean,na.rm=TRUE)
names(gradePropAmind) <- c('schoolGrade','gradePropAmind')
dta <- merge(dta,gradePropAmind,all=TRUE)
# group mean centers
dta$white_gmc <- groupMeanCenter(dta$white.x,dta$schoolGrade)
dta$black_gmc <- groupMeanCenter(dta$black.x,dta$schoolGrade)
dta$hispanic_gmc <- groupMeanCenter(dta$hispanic.x,dta$schoolGrade)
dta$asian_gmc <- groupMeanCenter(dta$asian.x,dta$schoolGrade)
dta$amind_gmc <- groupMeanCenter(dta$amind,dta$schoolGrade)
dta$other_gmc <- groupMeanCenter(dta$otherRace,dta$schoolGrade)

# More columns
dta$logIncome <- log(dta$income+1)
dta$hPropBelow_95 <- dta$hNumBelow_95/dta$gradeSize
dta$hPropAbove_95 <- dta$hNumAbove_95/dta$gradeSize
dta$bigOther <- !(dta$white.x|dta$black.x)
dta$black_x_propWhite <- dta$black.x*dta$commPropWhite
dta$normGradeSize <- standardize(dta$gradeSize)
dta$commPropWhite2 <- dta$commPropWhite**2
dta$hSizeCalc_90 <- dta$hNumBelow_90+dta$hNumAbove_90-1
dta$hSizeCalc_95 <- dta$hNumBelow_95+dta$hNumAbove_90-1
dta$hSizeCalc_75 <- dta$hNumBelow_75+dta$hNumAbove_90-1
dta$hSizeProp_75 <- dta$hSizeCalc_75/dta$gradeSize
dta$hSizeProp_90 <- dta$hSizeCalc_90/dta$gradeSize
dta$hSizeProp_95 <- dta$hSizeCalc_95/dta$gradeSize
#logistic tranform the [0,1] outcome vars
dta$propStatus_l <- logit(dta$propStatus+.001)
dta$hSizeProp_75_l <- logit(.999*dta$hSizeProp_75)
dta$hSizeProp_90_l <- logit(.999*dta$hSizeProp_90)
dta$hSizeProp_95_l <- logit(.999*dta$hSizeProp_95)

# standardize every reasonable column

for(colName in names(dta)){
    if(is.numeric(dta[[colName]])){
        dta[[paste(colName,'std',sep='_')]] <- standardize(dta[[colName]])
    }
}

write.csv(dta,file="") # /path/to/merged.csv
