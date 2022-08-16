from Model.DAO.Connection import Connection

def deleteUsersData(carsharingMode, usersNumberDay, distribution, duracaomin, duracaomax, distanciamin, distanciamax, numestacoes):
    conn = Connection().conn
    
    cur = conn.cursor()
    cur.execute("delete from USUARIOS_GERADOS " +
                "where modocarsharing = '" + carsharingMode + "' and numerousuarios = " + str(usersNumberDay) + " "
                "    and distribuicao = '" + distribution + "' and duracaomin = '" + str(duracaomin) + "' and duracaomax = '" + str(duracaomax) + "' "
                "    and distanciamin = '" + str(distanciamin) + "' and distanciamax = '" + str(distanciamax) + "' "
                "    and numestacoes = '" + str(numestacoes) + "'")
    conn.commit()
    
    cur.close()
    conn.close()
    
def loadUsersData(carsharingMode, usersNumberDay, distribution, duracaomin, duracaomax, distanciamin, distanciamax, numestacoes):
    conn = Connection().conn
    
    cur = conn.cursor()
    cur.execute("select id, localfim, horarioinicio, horariofim, distanciapercorrida " +
                "from USUARIOS_GERADOS " +
                "where modocarsharing = '" + carsharingMode + "' and numerousuarios = " + str(usersNumberDay) + " "
                "    and distribuicao = '" + distribution + "' and duracaomin = '" + str(duracaomin) + "' and duracaomax = '" + str(duracaomax) + "' "
                "    and distanciamin = '" + str(distanciamin) + "' and distanciamax = '" + str(distanciamax) + "' "
                "    and numestacoes = '" + str(numestacoes) + "' "
                "order by id")
    rows = cur.fetchall()
    cur.close()
    
    conn.close()
    
    return rows

def persistUsersData(users, carsharingMode, usersNumberDay, distribution, duracaomin, duracaomax, distanciamin, distanciamax, numestacoes):
    conn = Connection().conn
    maxDecimalDigits = 10
    
    sql = ("insert into USUARIOS_GERADOS (id, localinicio, localfim, horarioinicio, horariofim, " +
            "numerousuarios, distribuicao, modocarsharing, distanciapercorrida, duracaomin, duracaomax, distanciamin, distanciamax, numestacoes) " +
            "values ")
    
    for user in users:
        sql += "(" + str(user.id.split('_')[0]) + ", '" + user.stationStart.node.location + "', "
        sql += "'" + user.stationEnd.node.location + "', " + str(user.timeStart) + ", " + str(user.timeEnd) + ", "
        sql += str(usersNumberDay) + ", '" + distribution + "', '" + carsharingMode + "', " + str(round(user.drivenDistance, maxDecimalDigits)) + ", "
        sql += str(duracaomin) + ", " + str(duracaomax) + ", " + str(distanciamin) + ", " + str(distanciamax) + ", " + str(numestacoes) + "), "
    
    #Removing the last comma
    sql = sql[:-2] + " "
    
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()

    cur.close()
    conn.close()
    
        