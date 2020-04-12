# coding: utf-8

from flask import Flask, render_template, request
import json

app = Flask(__name__)

ARGS_ERR = -10;
DENIAL = -5;
N_ACCESSED = -10;

R_TEN = 1;
R_NTEN = -1;

W_AGARI = 1;
W_NAGARI = 0;
W_HOJU = -1;

KAZE = ["東","南","西","北"];


#初期化用辞書
init_myjson = {"player_list": ["","","",""],
"score_list": [[25000,25000,25000,25000]],
"config": {"oya": 0,"kaze": 0,"honba": 0,"kyotaku": 0},
"prev_config":{"oya": 0,"kaze": 0,"honba": 0,"kyotaku": 0}}
init_mybuffjson ={"ryukyoku": [-10,-10,-10,-10],"agari":[-10,-10,-10,-10],"score": [0,0,0,0],"reach": [0,0,0,0]}

# p_flag = True;

@app.route('/',methods=['GET'])
def chose():
    # req_house = request.args.get("house", type=int);
    # req_pname = request.args.get("name", type=str);
    #
    #
    # myfile = open('score.json','w')
    # json.dump(init_myjson, myfile, indent=2);
    # myfile.close();
    return render_template('index.html');


@app.route('/send_score', methods=['GET'])
def input():
    req_house = request.args.get("house", type=int);
    req_pname = request.args.get("name", type=str);

    myfile = open('score.json','r');
    myjson = json.load(myfile);
    myfile.close();
    myfile = open('score.json','w')
    myjson["player_list"][req_house] = req_pname;
    json.dump(myjson, myfile, indent=2);
    myfile.close();
    return render_template('send_score.html',name=req_pname, house=req_house);

@app.route('/show_score', methods=['GET'])
def send():
#req設定
    req_house = request.args.get('house', type=int);
    req_pname = request.args.get("name", type=str);
    req_reach = request.args.get('reach',type=int);
    req_ryukyoku = request.args.get('ryukyoku', type=int);
    req_agari = request.args.get('agari', type=int);
    req_score = request.args.get('score', type=int);


#arg変数初期値
    args_p0 = 0;
    args_p1 = 0;
    args_p2 = 0;
    args_p3 = 0;

    args_kaze = "";
    args_oya = 0;
    args_honba = 0;
    args_kyotaku = 0;
    args_kyoku = 1;
#バッファ変数初期値
    buff_score = [0,0, 0,0];


#フラグ設定

    agari = False;

#読み込み
    mybufffile = open('buff.json','r');
    mybuffjson = json.load(mybufffile);
    mybufffile.close();

    myfile = open('score.json','r');
    myjson = json.load(myfile)
    myfile.close();

#立直
    mybuffjson["reach"][req_house] = req_reach;

#req変数読み込み
    mybuffjson["ryukyoku"][req_house] = req_ryukyoku;
    mybuffjson["agari"][req_house] = req_agari;
    if req_agari == W_AGARI:
        mybuffjson["score"][req_house] = req_score;



#buff.jsonへの反映
    mybufffile = open('buff.json','w')
    json.dump(mybuffjson, mybufffile, indent=2);
    mybufffile.close();

#最後にアクセスしたかどうか
    last_flag = True;
    last_flag = (N_ACCESSED in mybuffjson["ryukyoku"]) or (N_ACCESSED in mybuffjson["agari"]);

#最後にアクセスしていた場合
    if not last_flag:
    #読み込み


        myjson["prev_config"] = myjson["config"];
        myjson["config"]= {"oya": 0,"kaze": 0,"honba": 0,"kyotaku": 0};
    #変数設定
        oya = myjson["config"]["oya"];
        honba = myjson["config"]["honba"];
        kyotaku = myjson["config"]["kyotaku"];
        player_id = str(req_house);
        myscore = req_score;
        buff_score = mybuffjson["score"];


    #流局の場合
        if req_agari == DENIAL:
            myjson["config"]["honba"] += 1;
            nb_tenpai = mybuffjson["ryukyoku"].count(R_TEN);

            if  (nb_tenpai != 4) and (nb_tenpai != 0):  #罰符処理
                nb_noten = 4 - nb_tenpai;
                bappu = int(3000/nb_noten);
                recieve = int(3000/nb_tenpai);
                for i in range(0,4):
                    if mybuffjson["ryukyoku"][i] == R_NTEN:
                        buff_score[i] -= bappu;
                    else:
                        buff_score[i] += recieve;
        #連荘制御
            if mybuffjson["ryukyoku"][oya] == R_NTEN:
                myjson["config"]["oya"] = (myjson["config"]["oya"]+1) % 3;


    #アガリの場合
        elif req_ryukyoku == DENIAL:
            agari = mybuffjson["agari"].index(W_AGARI);

        #連荘制御
            if oya == agari:
                myjson["config"]["honba"] += 1;
            else:
                myjson["config"]["oya"] = (myjson["config"]["oya"]+1)%3;
                myjson["config"]["honba"] = 0;

        #ロンアガリの時
            if W_HOJU in mybuffjson["agari"]:
                hoju = mybuffjson["agari"].index(W_HOJU);
                buff_score[hoju] -= (mybuffjson["score"][agari]+honba*300);
        #ツモアガリの時
            else:
            #親あがり
                if agari == oya :
                    payment = int(mybuffjson["score"][agari]/3);
                    for i in range(0,4):
                        if mybuffjson["agari"][i] == W_NAGARI:
                            buff_score[i] -= (payment+honba*100);
            #子上がり
                else:
                    myjson["config"]["honba"] = 0;
                    payment = int(mybuffjson["score"][agari]/4);
                    for i in range(0,4):
                        if mybuffjson["agari"][i] == W_NAGARI:
                        #親の点数
                            if i == oya:
                                buff_score[i] -=  (2*payment+honba*100);
                        #この点数
                            else:
                                buff_score[i] -= (payment+honba*100);


        #立直処理
            for i in range(0,4):
                buff_score[i] -= (mybuffjson["reach"][i]*1000);
                myjson["config"]["kyotaku"] += mybuffjson["reach"][i]; # 供託
            kyotaku = myjson["config"]["kyotaku"];


        #積み棒、供託
            buff_score[agari] += (honba*300 + kyotaku*1000);
        #供託回収
            myjson["config"]["kyotaku"] = 0;

    #合算
        for i in range(0,4):
            buff_score[i] += myjson['score_list'][-1][i];


    #点数反映
        # myjson["score_list"][0][req_house] = myscore;
        myjson['score_list'].append(buff_score);

        myfile = open('score.json','w')
        json.dump(myjson, myfile, indent=2);
        myfile.close();
    # buff初期化
        mybufffile = open('buff.json','w')
        json.dump(init_mybuffjson, mybufffile, indent=2);
        mybufffile.close();
    #引数設定
        args_kaze = KAZE[myjson["prev_config"]["kaze"]];
        args_oya = myjson["prev_config"]["oya"];
        args_kyoku = args_oya+1;

        args_honba = myjson["prev_config"]["honba"];

        args_kyotaku = myjson["config"]["kyotaku"];
    else:
        pass;

#引数設定
    current_scorelist = myjson["score_list"][-1];
    args_p0 = current_scorelist[args_oya];
    args_p1 = current_scorelist[(args_oya+1)%4];
    args_p2 = current_scorelist[(args_oya+2)%4];
    args_p3 = current_scorelist[(args_oya+3)%4];
    args_ph = KAZE[req_house];




    return render_template('show_score.html', p0=args_p0, p1=args_p1, p2=args_p2, p3=args_p3,
        kyoku=args_oya+1,honba=args_honba,name=req_pname, house_wind=args_ph, house=req_house)


@app.route('/test',methods=['GET'])
def test():
    return render_template('index.html');


@app.route('/finish',methods=['GET'])
def finish():
    return render_template('finish.html');
@app.route('/init', methods=['GET'])
def init():

    mybufffile = open('/Users/hagayuuya/Desktop/mjscore/buff.json','w')
    json.dump(init_mybuffjson, mybufffile, indent=2);
    mybufffile.close();

    myfile = open('/Users/hagayuuya/Desktop/mjscore/score.json','w')
    json.dump(init_myjson, myfile, indent=2);
    myfile.close();
    return render_template('index.html')

@app.route('/reload', methods=['GET'])
def reload():
    myfile = open('score.json','r');
    myjson = json.load(myfile)
    myfile.close();
    req_house = request.args.get('house', type=int);
    req_pname = myjson["player_list"][req_house];
    args_kaze = KAZE[myjson["prev_config"]["kaze"]];
    args_oya = myjson["prev_config"]["oya"];
    args_kyoku = args_oya+1;

    args_honba = myjson["prev_config"]["honba"];

    args_kyotaku = myjson["config"]["kyotaku"];
    current_scorelist = myjson["score_list"][-1];
    args_p0 = current_scorelist[args_oya];
    args_p1 = current_scorelist[(args_oya+1)%4];
    args_p2 = current_scorelist[(args_oya+2)%4];
    args_p3 = current_scorelist[(args_oya+3)%4];
    args_ph = KAZE[req_house];
    return render_template('show_score.html', p0=args_p0, p1=args_p1, p2=args_p2, p3=args_p3,
    kyoku=args_oya+1,honba=args_honba,name=req_pname, house_wind=args_ph, house=req_house)


if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)
