// *********************** makeenviroplots ****************
//             - author: H. Neal   date: 2015
// ********************************************************
int makeenviroplots(char* label, int ivar, float minday,float maxday,float hmin, float hmax)
{

  gROOT->Reset();

#include <iostream.h>
#include <stdio.h>
#include <fcntl.h>

  const int NBINS=40;

  FILE  *fp;
  int   i, iline=0;
  char  buff[300];

  time_t unow = time(0);
  time_t now = unow;
  gStyle->SetPadGridX(1);
  gStyle->SetPadGridY(1);
  gStyle->SetGridWidth(3);
  gStyle->SetTitleBorderSize(0.);
  gStyle->SetTitleX(0.5);
  gStyle->SetTitleAlign(23);
 
  gStyle->SetLabelSize(0.05,"y");
  gStyle->SetFuncColor(4);
  gStyle->SetFuncWidth(2);
  gStyle->SetAxisColor(1);
  gStyle->SetPadLeftMargin(0.15);
  //  gStyle->SetOptFit(1111);
  gStyle->SetOptFit(0000);
  gStyle->SetErrorX(0.01);
  gStyle->SetTextFont(12);
  
  char buff[100];
//  sprintf(buff,"comb_hist.gif");
//  TPostScript ps(buff,-111);


  TH1F *runhst[5];
  int nday = (maxday-minday);
  int ndiv = nday/(int(nday/20)+1);
  //  gStyle->SetNdivisions(ndiv,"x");

  runhst[0] = new TH1F("g1","Temperature vs, Time",144.0*(maxday-minday),now+minday*86400,now+maxday*86400);


  Double_t xvals[5][20000],yvals[5][20000];
  int nvals[5];

  time_t now = time(0);
  char file_in[80];

  int idat=0;
  sprintf(file_in,"nbtab.dat");
  if ((fp=fopen(file_in,"r"))==NULL) {
    exit(0);
  }
  fillgraph(fp,nvals,xvals,yvals,idat,now,ivar,runhst[idat]);
  fclose(fp);
  //  runhst[idat] = new TGraph(nvals[idat],xvals[idat],yvals[idat]);
  runhst[idat]->SetLineColor(2);
  runhst[idat]->SetMarkerColor(2);
  runhst[idat]->SetMarkerStyle(20);

  c1 = new TCanvas("c1"," ",1000,700);

  //  c1->SetFillStyle(4000);
  //  c1->SetFillColor(0);
  //  c1->Divide(3,3,0.001,0.001);
  c1->SetLineColor(2);


  int igrphidx[5]={0,2,1,3,4};


  THStack *stackedhist=  new THStack("hs1","blah");
  for (Int_t idx=0; idx<=0; idx++) {
    int igrph = igrphidx[idx];
    //    if (idx>0) runhst[igrph]->Add(runhst[igrphidx[idx-1]],EV,1.0,1.0);

    char dbuff[80];

    sprintf(dbuff,"Date (updated on %s)",ctime(&unow));

    cout << "igrph=" << igrph << endl;

    //    if (idx==0) runhst[igrph]->Draw("h");
    //    else if (nvals[igrph]>0) runhst[igrph]->Draw("h,same");
    stackedhist->Add(runhst[igrph]);
    cout << "after runhst prep" << endl;
  }
  stackedhist->Draw("p");
  stackedhist->GetXaxis()->SetTitle(dbuff);
  strcpy(dbuff,label);
  stackedhist->GetYaxis()->SetTitle(dbuff);
  //stackedhist->GetXaxis()->SetTitleSize(0.08);
  stackedhist->GetXaxis()->SetLabelSize(0.025);
  //    stackedhist->GetXaxis()->SetTitleOffset(0.);
  stackedhist->GetYaxis()->SetTitleOffset(2.0);
  stackedhist->GetXaxis()->SetLabelOffset(0.001);
  stackedhist->GetXaxis()->SetTimeFormat("%d-%H:%M%F1970-01-01 00:00:00");
  //    runhst[irel][igrph]->GetYaxis()->SetNoExponent(1);
  stackedhist->GetXaxis()->SetTimeDisplay(1);

  char titl[80];
  sprintf(titl,"LSST Cleanroom");
  stackedhist->SetTitle(titl);
  stackedhist->SetMinimum(hmin);
  stackedhist->SetMaximum(hmax);
  gStyle->SetTitleAlign(23);
  
  gPad->Modified();

  cout << "after stackedhist->Draw();" << endl;


  char outfn[80];
  sprintf(outfn,"enviro_%s.png",label);
  c1->Print(outfn);
  return(1);
}

void fillgraph(FILE *fp,int nvals[5],Double_t xvals[5][20000],Double_t yvals[5][20000],
	       int index,time_t now,int ivar,TH1F *runhstf)
{
  cout << " fillgraph: index=" << index << endl;
  nvals[index]=0;
  while (!feof(fp)) {
    int date,yr,mo,dy,hr,mn,sec,prepared,submitted,done;
    float ok[4];
    char inbuff[300];
    fgets(inbuff,290,fp);

    //    printf("inbuff = %s\n",inbuff);
    sscanf(inbuff,"%d %f %f %f",&date,&ok[0],&ok[1],&ok[2]);
    cout << " date = " << date << " ok = " << ok[ivar] << endl;
    float day=date;
    cout << " day = " << day << endl;
    nvals[index]++;
    xvals[index][nvals[index]-1]=day;
    yvals[index][nvals[index]-1]=ok[ivar];
    runhstf->Fill(day,ok[ivar]);
  }
  return;
}
